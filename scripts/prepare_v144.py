#!/usr/bin/env python3
"""Ajustar la portada y retirar solo las prendas de muestra intactas."""
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'updates/app-ui.html'
s=p.read_text(encoding='utf8')
if '/* Portada adaptable 1.4.4 */' in s: raise SystemExit(0)
for a,b in [('items:clone(ITEMS_SEED)','items:[]'),('looks:clone(LOOKS_SEED)','looks:[]'),('loans:LOANS_SEED()','loans:[]')]:
    assert s.count(a)==1,a
    s=s.replace(a,b,1)
assert s.count(';return o}catch(e){return seed()}')==1
s=s.replace(';return o}catch(e){return seed()}',';return quitarMuestras(o)}catch(e){return seed()}',1)
migration="""
function quitarMuestras(o){
  const ids=new Set();
  for(const item of o.items){
    const e=ITEMS_SEED.find(x=>x.id===item.id);
    if(e&&['id','name','category','wardrobe','spot','size','color','season','notes','favorite','donate']
        .every(k=>item[k]===e[k])&&!item.photo&&JSON.stringify(item.occasions||[])===JSON.stringify(e.occasions||[]))ids.add(item.id);
  }
  const items=o.items.filter(x=>!ids.has(x.id));
  const looks=o.looks.filter(x=>{
    const e=LOOKS_SEED.find(y=>y.id===x.id);
    return !(e&&x.name===e.name&&x.occasion===e.occasion&&JSON.stringify(x.itemIds||[])===JSON.stringify(e.itemIds));
  });
  const loans=o.loans.filter(x=>!(ids.has(x.itemId)&&
    ['ejemplo-prestamo-1','ejemplo-prestamo-2','ejemplo-prestamo-3'].includes(x.id)
    &&String(x.person||'').includes('(ejemplo)')));
  if(items.length===o.items.length&&looks.length===o.looks.length&&loans.length===o.loans.length)return o;
  const next={...o,items,looks,loans};
  try{localStorage.setItem(STORAGE_KEY,JSON.stringify(next));return next}catch(_){return o}
}
"""
assert s.count('function load(){')==1
s=s.replace('function load(){',migration+'function load(){',1)
first='<div class="section-head"><h3 class="section-title">Demostración</h3></div>'
assert s.count(first)==1
a=s.index(first);b=s.index('<div class="banner-tiny">',a)
assert 0<b-a<1200
s=s[:a]+s[b:]
a=s.index('function resetDemo(){');b=s.index('function clearDemo(){',a)
assert 0<b-a<700
s=s[:a]+s[b:]
css="""
/* Portada adaptable 1.4.4 */
.home-page .hero.studio-hero.home-hero{height:clamp(232px,66vw,278px)!important;min-height:clamp(232px,66vw,278px)!important}
.home-page .hero.home-hero .mother-hero-art{top:0!important;right:0!important;bottom:0!important;width:52%!important;height:100%!important}
.home-page .hero.home-hero .mother-hero-photo{position:static!important;display:block!important;width:100%!important;height:100%!important;max-width:none!important;max-height:none!important;object-fit:contain!important;object-position:bottom right!important;transform:none!important}
@media(max-width:355px){.home-page .hero.studio-hero.home-hero{height:232px!important;min-height:232px!important}.home-page .hero.home-hero .mother-hero-art{width:53%!important;height:100%!important}.home-page .hero.home-hero .mother-hero-photo{position:static!important;width:100%!important;height:100%!important}}
"""
s=s.replace('</style>',css+'</style>',1)
s=s.replace('EL ARMARIO DE MARÍA JOSÉ · v1.0 ·','EL ARMARIO DE MARÍA JOSÉ · v1.4.4 ·',1)
assert 'function quitarMuestras(o)' in s and 'items:[],wardrobes:[...WARDROBE_SEED]' in s
p.write_text(s,encoding='utf8')
print('Portada adaptable; datos iniciales vacíos y limpieza segura.')
