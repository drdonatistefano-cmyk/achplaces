from playwright.sync_api import sync_playwright
url="http://localhost:8765/index.html"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"]);errs=[]
    pg=b.new_page(viewport={"width":390,"height":844},device_scale_factor=2);pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(url);pg.wait_for_function("!document.getElementById('count').textContent.includes('Caricamento')",timeout=20000)
    st=lambda t:print(t,"|",pg.inner_text("#count"),"| R:",pg.inner_text("#reg-val").replace("\n"," "),"| P:",pg.inner_text("#prov-val").replace("\n"," "),"| C:",pg.inner_text("#com-val").replace("\n"," "),"| pills:",pg.locator("#active .apill").all_inner_texts())
    st("start")
    pg.click("#reg-btn");pg.wait_for_timeout(150);pg.screenshot(path="/tmp/v25_reg.png")
    pg.locator('#reg-list .mopt[data-r="toscana"]').click();pg.wait_for_timeout(250);st("toscana")
    pg.locator('#reg-list .mopt[data-r="emilia-romagna"]').click();pg.wait_for_timeout(250);st("+ER")
    pg.locator('#reg-list .mopt[data-r="toscana"]').click();pg.wait_for_timeout(250);st("-TOS")
    pg.click("#prov-btn");pg.locator('#prov-list .mopt[data-p="RA"]').click();pg.wait_for_timeout(250);st("prov RA")
    pg.click("#reg-btn");pg.locator('#reg-list .mopt[data-r="toscana"]').click();pg.wait_for_timeout(250);st("RA+TOS")
    pg.click("#reg-all");pg.wait_for_timeout(250);st("tutte")
    pg.goto(url+"#ravenna-ra");pg.wait_for_timeout(300);pg.wait_for_function("!document.getElementById('count').textContent.includes('Caricamento')",timeout=20000);st("comune");pg.click("#resetbtn");pg.wait_for_timeout(250);st("reset")
    pg.keyboard.press("Escape");pg.screenshot(path="/tmp/v25_ip.png",clip={"x":0,"y":0,"width":390,"height":420})
    print("ERR",errs);b.close()
