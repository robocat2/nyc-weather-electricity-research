'use strict';
(() => {
  const data = window.RESEARCH;
  if (!data) return;
  const ns = 'http://www.w3.org/2000/svg';
  const usd = n => (n < 0 ? '−' : '') + '$' + Math.abs(n).toLocaleString('en-US', {minimumFractionDigits:2,maximumFractionDigits:2});
  const number = n => n.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});
  function element(tag,attrs={},text){const e=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,String(v));if(text!==undefined)e.textContent=text;return e;}
  function bars(id,values,unit){
    const host=document.getElementById(id);if(!host)return;
    const draw=()=>{
      const width=Math.max(host.clientWidth,200),row=55,height=values.length*row+25;
      const svg=element('svg',{viewBox:`0 0 ${width} ${height}`,role:'img','aria-label':values.map(v=>`${v.label}: ${number(v.value)} ${unit}`).join('; ')});
      svg.append(element('title',{},`Mean absolute error (${unit}); lower is better`));
      const max=Math.max(...values.map(v=>v.value))*1.04;
      values.forEach((v,i)=>{const y=i*row;
        svg.append(element('text',{x:0,y:y+13,fill:'#526367','font-size':11.5,'font-family':'inherit'},v.label));
        svg.append(element('text',{x:width,y:y+13,'text-anchor':'end',fill:'#182d32','font-size':12,'font-family':'inherit'},number(v.value)));
        svg.append(element('rect',{x:0,y:y+25,width,height:8,fill:'#e2e6e0'}));
        svg.append(element('rect',{x:0,y:y+25,width:Math.max(0,width*v.value/max),height:8,fill:v.selected?'#20695e':'#9da9a5'}));
      });
      svg.append(element('text',{x:0,y:height-2,fill:'#526367','font-size':10.5,'font-family':'inherit'},`MAE · ${unit} · lower is better · bars start at zero`));
      host.replaceChildren(svg);
    };
    new ResizeObserver(draw).observe(host);draw();
  }
  const modelLabels={calendar:'Calendar-only',linear:'Linear temperature',spline:'Temperature spline'};
  bars('hero-bars',data.price.filter(v=>v.name!=='linear').map(v=>({label:modelLabels[v.name],value:v.mae,selected:v.name==='spline'})),'$/MWh');
  bars('demand-bars',data.demand.map(v=>({label:modelLabels[v.name],value:v.mae,selected:v.name==='spline'})),'MW');
  bars('price-bars',data.price.map(v=>({label:modelLabels[v.name],value:v.mae,selected:v.name==='spline'})),'$/MWh');
  document.querySelector('[data-value="priceGain"]').textContent=data.priceGain.toFixed(1)+'%';
  document.querySelectorAll('[data-repo]').forEach(a=>a.href=data.repository);
  const tbody=document.getElementById('strategy-table');
  const strategyNames={linear:'Weather rule · selected',calendar:'Calendar-only',always_load:'Always virtual load',flat:'Flat'};
  for(const key of ['linear','calendar','always_load','flat']){
    const row=data.trading.find(x=>x.name===key),tr=document.createElement('tr');if(key==='linear')tr.className='selected-row';
    for(const value of [strategyNames[key],usd(row.total),usd(row.drawdown)]){const td=document.createElement('td');td.textContent=value;tr.append(td);}tbody.append(tr);
  }
  const chart=document.getElementById('equity-chart'),tooltip=document.getElementById('equity-tooltip');
  const colors={linear:'#8ad4bf',always_load:'#e2b66e',calendar:'#9dabb0'},names={linear:'Weather rule',always_load:'Always virtual load',calendar:'Calendar-only'};
  const visible=new Set(['linear','always_load','calendar']);
  const points=data.cumulative.map(d=>({...d,time:Date.parse(d.date+'T12:00:00Z')}));
  let drawChart;
  drawChart=()=>{
    const previous=chart.querySelector('svg');if(previous)previous.remove();tooltip.hidden=true;
    const w=Math.max(chart.clientWidth,250),h=w<500?255:330,m={left:54,right:14,top:17,bottom:35};
    const vals=points.flatMap(p=>Object.keys(names).map(k=>p[k]));vals.push(0);
    const vmin=Math.min(...vals),vmax=Math.max(...vals),pad=(vmax-vmin)*.1,min=vmin-pad,max=vmax+pad;
    const start=Date.parse('2025-01-01T12:00:00Z'),end=Date.parse('2025-12-31T12:00:00Z');
    const x=t=>m.left+(t-start)/(end-start)*(w-m.left-m.right),y=v=>m.top+(max-v)/(max-min)*(h-m.top-m.bottom);
    const svg=element('svg',{viewBox:`0 0 ${w} ${h}`,role:'img','aria-label':'Cumulative hypothetical gross payoff in 2025. Selected weather rule finishes at $1,020.96, always virtual load $1,384.92 and calendar-only $321.98. One June day dominates the selected rule’s total.'});
    svg.append(element('title',{},'Cumulative gross payoff, 2025 ($)'));
    const defs=element('defs'),clip=element('clipPath',{id:'equity-clip'});clip.append(element('rect',{x:m.left,y:m.top,width:w-m.left-m.right,height:h-m.top-m.bottom}));defs.append(clip);svg.append(defs);
    const step=1000,first=Math.ceil(min/step)*step;
    for(let value=first;value<=max;value+=step){
      svg.append(element('line',{x1:m.left,x2:w-m.right,y1:y(value),y2:y(value),stroke:value===0?'#8b9da0':'#39545a','stroke-width':value===0?1:0.6}));
      svg.append(element('text',{x:m.left-10,y:y(value)+4,'text-anchor':'end',fill:'#b7c7c6','font-size':10,'font-family':'inherit'},value===0?'$0':(value<0?'−':'')+'$'+Math.abs(value/1000)+'k'));
    }
    const ticks=w<500?[[0,'Jan'],[4,'May'],[8,'Sep'],[11,'Dec']]:[[0,'Jan'],[2,'Mar'],[4,'May'],[6,'Jul'],[8,'Sep'],[11,'Dec']];
    ticks.forEach(([month,label])=>svg.append(element('text',{x:x(Date.UTC(2025,month,month===11?31:1,12)),y:h-10,'text-anchor':month===11?'end':'start',fill:'#b7c7c6','font-size':11,'font-family':'inherit'},label)));
    svg.append(element('text',{x:m.left,y:10,fill:'#b7c7c6','font-size':10,'font-family':'inherit'},'Gross $'));
    const plot=element('g',{'clip-path':'url(#equity-clip)'});
    for(const key of Object.keys(names))if(visible.has(key))plot.append(element('path',{d:points.map((p,i)=>(i?'L':'M')+x(p.time).toFixed(2)+','+y(p[key]).toFixed(2)).join(' '),fill:'none',stroke:colors[key],'stroke-width':key==='linear'?2.6:1.7,'data-line':key}));
    const date=Date.parse('2025-06-24T12:00:00Z');
    plot.append(element('line',{x1:x(date),x2:x(date),y1:m.top,y2:h-m.bottom,stroke:'#6d898b','stroke-dasharray':'3 5','stroke-width':.8}));
    svg.append(plot);
    if(w>500)svg.append(element('text',{x:x(date)+7,y:m.top+12,fill:'#b7c7c6','font-size':10,'font-family':'inherit'},'June 24: extreme spread'));
    const guide=element('line',{y1:m.top,y2:h-m.bottom,stroke:'#d0e3dc','stroke-width':1,visibility:'hidden'});svg.append(guide);
    const hit=element('rect',{x:m.left,y:m.top,width:w-m.left-m.right,height:h-m.top-m.bottom,fill:'transparent','aria-hidden':'true'});svg.append(hit);
    const show=event=>{
      const bounds=svg.getBoundingClientRect(),pointerX=(event.clientX-bounds.left)*w/bounds.width;
      const target=start+(pointerX-m.left)/(w-m.left-m.right)*(end-start);
      let best=points[0];for(const p of points)if(Math.abs(p.time-target)<Math.abs(best.time-target))best=p;
      guide.setAttribute('x1',x(best.time));guide.setAttribute('x2',x(best.time));guide.setAttribute('visibility','visible');
      tooltip.replaceChildren();const title=document.createElement('strong');title.textContent=new Date(best.time).toLocaleDateString('en-US',{year:'numeric',month:'short',day:'numeric',timeZone:'UTC'});tooltip.append(title);
      for(const key of Object.keys(names))if(visible.has(key)){const row=document.createElement('div');row.className='tooltip-row';const label=document.createElement('span'),value=document.createElement('span');label.textContent=names[key];value.textContent=usd(best[key]);row.append(label,value);tooltip.append(row);}
      tooltip.hidden=false;const pos=(x(best.time)/w)*chart.clientWidth;tooltip.style.left=Math.max(0,Math.min(chart.clientWidth-tooltip.offsetWidth,pos+12))+'px';tooltip.style.top='5px';
    };
    hit.addEventListener('pointermove',show);hit.addEventListener('click',show);
    hit.addEventListener('pointerleave',e=>{if(e.pointerType!=='touch'){tooltip.hidden=true;guide.setAttribute('visibility','hidden');}});
    chart.insertBefore(svg,tooltip);
  };
  document.querySelectorAll('[data-series]').forEach(button=>button.addEventListener('click',()=>{
    const key=button.dataset.series;if(visible.has(key)){if(visible.size===1)return;visible.delete(key);}else visible.add(key);
    document.querySelectorAll('[data-series]').forEach(b=>{const active=visible.has(b.dataset.series);b.setAttribute('aria-pressed',String(active));b.disabled=active&&visible.size===1;});drawChart();
  }));
  new ResizeObserver(drawChart).observe(chart);drawChart();
})();
