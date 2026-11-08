import base64, html
import streamlit as st
COLORS={"navy":"#082F5B","blue":"#0878C9","cyan":"#22C8C8","green":"#20AA58","green_light":"#54D65C","surface":"#F4F8FB","text":"#16324F","white":"#FFFFFF"}
PATHS={
 "portafolio":"M3 11.5 12 4l9 7.5V21h-6v-6H9v6H3z",
 "dashboard":"M4 19h3V9H4zm6 0h4V4h-4zm7 0h3V12h-3z",
 "inmuebles":"M4 21V5h10v16m0-10h6v10M7 8h2m2 0h1M7 12h2m2 0h1M7 16h2m2 0h1m5-2h2m-2 4h2",
 "espacios":"M5 4h14v16H5zm3 3h8v10H8zm2 8h4",
 "personas":"M8 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm8-1a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zM2 20c0-4 2.7-6 6-6s6 2 6 6m0-6c4 0 7 2 7 6",
 "usuarios":"M10 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM3 21c0-5 3-7 7-7 1.7 0 3.1.4 4.2 1.1M18 14l1 1 2-.2.7 1.8-1.6 1.2.1 2-1.8.8-1.3-1.5-2 .4-.8-1.8 1.5-1.3-.4-2 1.8-.8 1.2 1.6z",
 "finanzas":"M4 8c0-2 3-3 6-3s6 1 6 3-3 3-6 3-6-1-6-3zm0 0v4c0 2 3 3 6 3s6-1 6-3V8m-12 4v4c0 2 3 3 6 3m7-8v7m-2-5h4",
 "catalogos":"M5 4h14v16H5zm4 4h6m-6 4h6m-6 4h4",
 "configuracion":"M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7zm0-5 1 2.2 2.2.7 2-1 1.7 1.7-1 2 .7 2.2 2.2 1v2.4l-2.2 1-.7 2.2 1 2-1.7 1.7-2-1-2.2.7-1 2.2H10l-1-2.2-2.2-.7-2 1-1.7-1.7 1-2-.7-2.2-2.2-1v-2.4l2.2-1 .7-2.2-1-2L4.8 4l2 1 2.2-.7 1-2.2z",
 "auditoria":"M12 2 20 5v6c0 5-3.4 9.2-8 11-4.6-1.8-8-6-8-11V5zm-4 10 2.5 2.5L16 9",
 "logout":"M10 4H4v16h6m4-4 4-4-4-4m4 4H8"}
def svg(name,size=30):
    p=PATHS[name]; gid='csgrad_'+name; fid='csshadow_'+name
    green=name in {'personas','finanzas','auditoria'}
    c1='#59D85D' if green else '#1AC6E9'; c2='#20AA58' if green else '#0878C9'; c3='#087D45' if green else '#082F5B'
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" aria-hidden="true"><defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset=".55" stop-color="{c2}"/><stop offset="1" stop-color="{c3}"/></linearGradient><filter id="{fid}" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="1.2" stdDeviation=".75" flood-color="#082F5B" flood-opacity=".20"/></filter></defs><path d="{p}" fill="none" stroke="url(#{gid})" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" filter="url(#{fid})"/></svg>'

def data_icon(name): return 'data:image/svg+xml;base64,'+base64.b64encode(svg(name,24).encode()).decode()
def image_uri(data,mime='image/png'): return 'data:'+(mime or 'image/png')+';base64,'+base64.b64encode(bytes(data)).decode()
def logo(data,mime='image/png',max_width=320,max_height=None,alt='Condo-Smart'):
    if not data:return
    mh=f'max-height:{int(max_height)}px;' if max_height else ''
    st.markdown(f'<div class="cs-logo"><img src="{image_uri(data,mime)}" alt="{html.escape(alt)}" style="max-width:min(100%,{int(max_width)}px);width:auto;height:auto;{mh}object-fit:contain"/></div>',unsafe_allow_html=True)
def inject_theme():
    st.markdown('''<style>
    :root{--cs-navy:#082F5B;--cs-blue:#0878C9;--cs-cyan:#22C8C8;--cs-green:#20AA58;--cs-green-light:#54D65C;--cs-surface:#F4F8FB;--cs-text:#16324F;--cs-white:#FFF;--cs-radius:18px;--cs-shadow:0 16px 50px rgba(8,47,91,.12)}
    html,body,[class*="css"]{font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:var(--cs-text)}
    .stApp{background:linear-gradient(145deg,#f7fbfe 0%,#edf7f7 55%,#f7fbf7 100%)}
    [data-testid="stSidebar"]{background:rgba(255,255,255,.97);border-right:1px solid #dce8ef}
    [data-testid="stSidebar"] [data-testid="stImage"] img{object-fit:contain!important;height:auto!important}
    .cs-logo{text-align:center;margin:.25rem auto 1rem}.cs-logo img{display:block;margin:auto}
    .cs-login-title{text-align:center;color:var(--cs-navy);font-size:2rem;font-weight:800;margin:.25rem 0 0}.cs-login-sub{text-align:center;color:#61758a;margin:0 0 1rem}
    .cs-login-foot{text-align:center;color:#6d8295;font-size:.82rem;margin-top:1rem}.cs-login-foot b{color:var(--cs-navy)}
    .stButton>button,.stFormSubmitButton>button{border-radius:12px;border:0;font-weight:700}
    .stFormSubmitButton>button[kind="primary"]{background:linear-gradient(90deg,var(--cs-blue),var(--cs-green));color:white}
    [data-testid="stTextInputRootElement"]{border-radius:12px}
    .cs-nav a{display:flex;align-items:center;gap:12px;padding:10px 12px;margin:3px 0;border-radius:11px;color:#344f69;text-decoration:none;font-weight:550}.cs-nav a:hover{background:#eef7fb}.cs-nav a.active{background:linear-gradient(90deg,#e9f4ff,#edf9f2);color:var(--cs-blue);font-weight:750}.cs-nav img{width:23px;height:23px}
    .cs-user{border-top:1px solid #dbe6ed;margin-top:12px;padding:12px 6px;color:var(--cs-navy)}
    .cs-native-icon{height:38px;display:flex;align-items:center;justify-content:center}.cs-native-icon svg{width:24px;height:24px;display:block}
[data-testid="stSidebar"] .stButton>button{min-height:38px;text-align:left;justify-content:flex-start;padding:.35rem .6rem;border-radius:10px;box-shadow:none}
[data-testid="stSidebar"] .stButton>button[kind="secondary"]{background:transparent;border-color:transparent;color:#344f69}
[data-testid="stSidebar"] .stButton>button[kind="primary"]{background:linear-gradient(90deg,#e9f4ff,#edf9f2);border-color:transparent;color:#0878C9}
.cs-nav-icon,.cs-native-icon{width:34px;height:42px;display:inline-flex;align-items:center;justify-content:center;flex:0 0 34px}.cs-nav-icon svg,.cs-native-icon svg{display:block;width:30px;height:30px;overflow:visible}
.cs-designer-icon{width:58px!important;height:58px!important;object-fit:contain!important;object-position:center center!important;display:block!important;margin:0 auto!important;filter:none!important;border:0!important;background:transparent!important}
</style>''',unsafe_allow_html=True)

def menu_icon_uri(name):
    from pathlib import Path
    p=Path(__file__).resolve().parents[1]/"assets"/"brand"/"icons"/f"{name}.png"
    if not p.exists(): return ""
    return "data:image/png;base64,"+base64.b64encode(p.read_bytes()).decode()

def sidebar_nav(pages,current,user):
    selected=current
    for label,key,module in pages:
        ci,ct=st.sidebar.columns([0.18,0.82],vertical_alignment="center")
        with ci:
            uri=menu_icon_uri(key)
            if uri: st.markdown(f'<img class="cs-designer-icon" src="{uri}" alt="">',unsafe_allow_html=True)
        with ct:
            if st.button(label,key=f"cs_nav_{key}",use_container_width=True,type="primary" if key==current else "secondary"):
                selected=key
    st.sidebar.markdown(f'<div class="cs-user"><strong>{html.escape(str(user.get("nombre","Usuario")))}</strong><br><small>{html.escape(str(user.get("rol_global","")))}</small></div>',unsafe_allow_html=True)
    return selected
