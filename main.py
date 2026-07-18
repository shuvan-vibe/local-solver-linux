"""
Turnstile solver microservice using FastAPI and SeleniumBase UC mode.
Optimized for Linux execution (desktop & headless servers).
Uses Xvfb virtual display instead of headless mode to bypass Cloudflare detection.
"""

import os
import time
import logging
import traceback
from typing import Optional
import threading
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Local Turnstile Solver API")
solve_lock = threading.Lock()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SITEKEY = "0x4AAAAAADuXG2nt8DMgL_NF"
PAGEURL = "https://tma.foxigrow.com"

# JavaScript to inject a Turnstile widget and capture its token
INJECT_JS = f"""
(function() {{
    if (window.__turnstileInjected) return;
    window.__turnstileInjected = true;
    window.__turnstileToken = null;
    window.__turnstileError = null;
    window.__turnstileWidgetId = null;

    var container = document.createElement('div');
    container.id = '__cf_turnstile_solver';
    container.style.cssText = 'position:fixed;top:0;left:0;z-index:2147483647;background:white;padding:5px;';
    document.body.appendChild(container);

    var script = document.createElement('script');
    script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit&onload=__onTurnstileLoad';
    script.async = true;
    script.defer = true;

    window.__onTurnstileLoad = function() {{
        try {{
            var widgetId = window.turnstile.render('#__cf_turnstile_solver', {{
                sitekey: '{SITEKEY}',
                callback: function(token) {{
                    window.__turnstileToken = token;
                    console.log('[Solver] Token received: ' + token.slice(0, 20) + '...');
                }},
                'error-callback': function(code) {{
                    window.__turnstileError = String(code);
                }}
            }});
            window.__turnstileWidgetId = widgetId;
        }} catch(e) {{
            console.log('[Solver] Render error: ' + e);
        }}
    }};

    document.head.appendChild(script);
}})();
"""


global_sb_context = None
global_sb = None
solve_count = 0

def solve_turnstile() -> Optional[str]:
    """Navigate to target page, inject Turnstile, auto-solve, return token."""
    from seleniumbase import SB
    global global_sb_context, global_sb, solve_count

    try:
        # Restart browser if it's the first time, or if we've used it 20 times
        if global_sb is None or solve_count >= 20:
            logger.info(f"Browser state (count={solve_count}). Needs fresh browser.")
            if global_sb_context is not None:
                try:
                    global_sb_context.__exit__(None, None, None)
                except Exception:
                    pass
                global_sb = None
                global_sb_context = None
                time.sleep(1) # Allow process to die

            logger.info("Launching fresh SeleniumBase UC browser (Linux Stealth Mode)...")
            # Xvfb virtual display is started by start-solver.sh (display :99)
            # so the browser renders invisibly. We set xvfb=False here because
            # we manage the virtual display ourselves for maximum reliability.
            global_sb_context = SB(uc=True, xvfb=False, headless=False, locale_code="en")
            global_sb = global_sb_context.__enter__() # Get the actual SB instance
            solve_count = 0
            
            logger.info(f"Navigating to {PAGEURL}...")
            global_sb.open(PAGEURL)
        else:
            logger.info(f"Reusing existing browser (count={solve_count}). Refreshing page...")
            global_sb.refresh()

        solve_count += 1
        sb = global_sb

        # Wait for the page body to exist so we can append the Turnstile container
        sb.wait_for_element("body", timeout=30)

        logger.info("Injecting Turnstile widget...")
        try:
            sb.execute_script(INJECT_JS)
        except Exception as e:
            logger.error(f"Failed to inject widget: {e}")
            return None

        # Wait for the Turnstile API script to load (it loads async)
        logger.info("Waiting for Turnstile API to load...")
        api_loaded = False
        for attempt in range(30):  # Up to 15 seconds
            time.sleep(0.5)
            try:
                status = sb.execute_script("""(function(){
                    return {
                        turnstileExists: typeof window.turnstile !== 'undefined',
                        injected: !!window.__turnstileInjected,
                        token: window.__turnstileToken || null,
                        error: window.__turnstileError || null
                    };
                })()""")
                
                if status and status.get('turnstileExists'):
                    api_loaded = True
                    logger.info("Turnstile API loaded!")
                    time.sleep(3)  # Extra time for iframe to render
                    break
                if status and status.get('token'):
                    return status['token']
            except Exception:
                pass

        if not api_loaded:
            logger.error("Turnstile API script never loaded!")

        logger.info("Waiting for Turnstile token (up to 30s)...")
        for i in range(60):
            time.sleep(0.5)
            try:
                token = sb.execute_script("window.__turnstileToken || null")
                if token and len(str(token)) > 10:
                    logger.info(f"SUCCESS! Token obtained in {(i + 1) * 0.5:.1f}s")
                    return token

                error = sb.execute_script("window.__turnstileError || null")
                if error:
                    logger.warning(f"Turnstile widget reported error: {error} (Waiting for auto-retry...)")
                    sb.execute_script("window.__turnstileError = null;")
                    
                # If 8 seconds have passed and no token, try clicking the widget!
                if i == 16:
                    logger.info("Attempting to click the Turnstile widget...")
                    try:
                        # Click the container div that holds the widget (no need to switch frames)
                        sb.uc_click("#__cf_turnstile_solver")
                        logger.info("Click successful, waiting for token...")
                    except Exception as e:
                        logger.warning(f"Could not click widget: {e}")
            except Exception:
                pass

        logger.error("Timeout: No Turnstile token after 30s")
        # Force browser restart on timeout to avoid getting stuck
        raise Exception("Turnstile timeout")
        
    except Exception as e:
        logger.error(f"Error during solve: {e}")
        logger.error(traceback.format_exc())
        # Force teardown so the next request gets a clean browser
        if global_sb_context is not None:
            try:
                global_sb_context.__exit__(None, None, None)
            except Exception:
                pass
            global_sb = None
            global_sb_context = None
        return None

@app.on_event("shutdown")
def shutdown_event():
    """Ensure the browser closes when the server shuts down."""
    global global_sb_context, global_sb
    if global_sb_context is not None:
        logger.info("Shutting down global browser instance...")
        try:
            global_sb_context.__exit__(None, None, None)
        except:
            pass
        global_sb = None
        global_sb_context = None

@app.get("/")
def root():
    return {"status": "ok", "service": "Local Turnstile Solver API"}

@app.get("/getToken")
@app.get("/gettoken")
def get_token():
    """Solve a Turnstile captcha and return the token. Auto-retries up to 3 times."""
    with solve_lock:
        max_retries = 3
        start_time = time.time()

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Solve attempt {attempt}/{max_retries}...")
                token = solve_turnstile()

                if token:
                    elapsed = time.time() - start_time
                    return JSONResponse(content={
                        "success": True,
                        "token": token,
                        "elapsed_s": round(elapsed, 2),
                        "attempts": attempt
                    })
                else:
                    logger.warning(f"Attempt {attempt} failed, {'retrying...' if attempt < max_retries else 'giving up.'}")
            except Exception as e:
                logger.error(f"Attempt {attempt} error: {e}")

        elapsed = time.time() - start_time
        return JSONResponse(
            content={"success": False, "error": "Failed after all retries", "elapsed_s": round(elapsed, 2)},
            status_code=503
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
