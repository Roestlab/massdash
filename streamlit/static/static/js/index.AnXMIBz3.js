import{x as c,a4 as l,r as i,j as e,a$ as p}from"./index.DMxc2XFp.js";import{P as d,R as f}from"./Particles.BfWfv0Aw.js";const g=""+new URL("../media/flake-0.DgWaVvm5.png",import.meta.url).href,u=""+new URL("../media/flake-1.B2r5AHMK.png",import.meta.url).href,x=""+new URL("../media/flake-2.BnWSExPC.png",import.meta.url).href,o=150,s=150,E=10,S=90,_=4e3,a=(t,n=0)=>Math.random()*(t-n)+n,w=()=>l(`from{transform:translateY(0)
      rotateX(`,a(360),`deg)
      rotateY(`,a(360),`deg)
      rotateZ(`,a(360),"deg);}to{transform:translateY(calc(100vh + ",o,`px))
      rotateX(0)
      rotateY(0)
      rotateZ(0);}`),A=c("img",{target:"es7rdur0"})(({theme:t})=>({position:"fixed",top:`${-o}px`,marginLeft:`${-s/2}px`,zIndex:t.zIndices.balloons,left:`${a(S,E)}vw`,animationDelay:`${a(_)}ms`,height:`${o}px`,width:`${s}px`,pointerEvents:"none",animationDuration:"3000ms",animationName:w(),animationTimingFunction:"ease-in",animationDirection:"normal",animationIterationCount:1,opacity:1})),I=100,m=[g,u,x],M=m.length,h=i.memo(({particleType:t,resourceCrossOriginMode:n})=>{const r=m[t];return e(A,{src:r,crossOrigin:p(n,r)})}),P=function({scriptRunId:n}){return e(f,{children:e(d,{className:"stSnow","data-testid":"stSnow",scriptRunId:n,numParticleTypes:M,numParticles:I,ParticleComponent:h})})},L=i.memo(P);export{I as NUM_FLAKES,L as default};
