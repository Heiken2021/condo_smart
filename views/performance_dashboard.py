import hashlib
import json
import time

import pandas as pd
import streamlit as st

from agents.performance_agent import (
    PerformanceAgent,
    sanitize_snapshot,
)
from services.performance import summary,modules,history,trends,by_operation,performance_health,diagnostic_breakdown,performance_agent_interpretation,performance_snapshot


fragment = getattr(st, 'fragment', lambda **kwargs: (lambda func: func))


AI_REFRESH_SECONDS = 60
AI_CACHE_TTL_SECONDS = 300
AI_CACHE_RESULT_KEY = 'performance_ai_cached_result'
AI_CACHE_FINGERPRINT_KEY = 'performance_ai_cached_fingerprint'
AI_CACHE_TIME_KEY = 'performance_ai_cached_at'


def _performance_ai_fingerprint(snapshot):
    payload=sanitize_snapshot(snapshot)
    serialized=json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(
        serialized.encode('utf-8')
    ).hexdigest()


def _performance_ai_result(
    snapshot,
    local_interpretation,
):
    fingerprint=_performance_ai_fingerprint(snapshot)
    cached_result=st.session_state.get(
        AI_CACHE_RESULT_KEY
    )
    cached_fingerprint=st.session_state.get(
        AI_CACHE_FINGERPRINT_KEY
    )
    cached_at=float(
        st.session_state.get(AI_CACHE_TIME_KEY, 0)
        or 0
    )
    cache_age=max(0, time.time()-cached_at)

    cache_valid=(
        cached_result is not None
        and cached_fingerprint == fingerprint
        and cache_age < AI_CACHE_TTL_SECONDS
    )

    if cache_valid:
        return cached_result, True, cache_age

    result=PerformanceAgent().analyze(
        snapshot,
        local_interpretation,
    )

    st.session_state[AI_CACHE_RESULT_KEY]=result
    st.session_state[AI_CACHE_FINGERPRINT_KEY]=fingerprint
    st.session_state[AI_CACHE_TIME_KEY]=time.time()

    return result, False, 0.0


def render_live_performance_agent(days,module,limit,enabled=False):
    run_every=(
        f'{AI_REFRESH_SECONDS}s'
        if enabled
        else None
    )

    @fragment(run_every=run_every)
    def _agent_fragment():
        snapshot=performance_snapshot(days,module,limit)
        local_interpretation=performance_agent_interpretation(
            days,
            module,
            snapshot,
        )

        cache_hit=False
        cache_age=0.0

        if enabled:
            agent_result,cache_hit,cache_age=(
                _performance_ai_result(
                    snapshot,
                    local_interpretation,
                )
            )
        else:
            agent_result={
                'source': 'LOCAL',
                'prompt_version': 'performance-v1',
                'fallback_reason': 'AGENTE_IA_APAGADO',
                'generated_at': local_interpretation['generated_at'],
                'analysis': None,
            }

        source=agent_result['source']
        prompt_version=agent_result['prompt_version']
        fallback_reason=agent_result.get('fallback_reason')
        analysis=agent_result.get('analysis')

        if analysis is None:
            interpretation=local_interpretation
            probable_causes=[]
            priority={
                'OPTIMO': 'BAJA',
                'ATENCION': 'MEDIA',
                'CRITICO': 'CRITICA',
                'SIN_DATOS': 'BAJA',
            }.get(interpretation['level'], 'MEDIA')
            requires_human_review=(
                interpretation['level'] == 'CRITICO'
            )
        else:
            interpretation={
                'level': analysis.level,
                'confidence': analysis.confidence,
                'headline': analysis.headline,
                'summary': analysis.summary,
                'evidence': analysis.evidence,
                'recommendations': analysis.recommendations,
                'generated_at': agent_result['generated_at'],
            }
            probable_causes=analysis.probable_causes
            priority=analysis.priority
            requires_human_review=analysis.requires_human_review

        colors={
            'OPTIMO':'#16A34A',
            'ATENCION':'#F59E0B',
            'CRITICO':'#DC2626',
            'SIN_DATOS':'#64748B',
        }
        color=colors.get(
            interpretation['level'],
            '#64748B',
        )
        source_color='#2563EB' if source == 'IA' else '#64748B'

        st.markdown('### Agente De Interpretación En Vivo')

        st.markdown(
            f"""
            <div style="display:flex;gap:8px;align-items:center;
                        flex-wrap:wrap;margin-bottom:10px;">
                <span style="background:{source_color};color:#FFFFFF;
                             border-radius:999px;padding:4px 10px;
                             font-size:.78rem;font-weight:800;">
                    FUENTE: {source}
                </span>
                <span style="background:#E2E8F0;color:#334155;
                             border-radius:999px;padding:4px 10px;
                             font-size:.78rem;font-weight:700;">
                    PROMPT: {prompt_version}
                </span>
                <span style="background:#F1F5F9;color:#475569;
                             border-radius:999px;padding:4px 10px;
                             font-size:.78rem;font-weight:700;">
                    PRIORIDAD: {priority}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div style="border-left:6px solid {color};
                        background:#FFFFFF;border-radius:12px;
                        padding:16px 18px;margin-bottom:12px;
                        box-shadow:0 3px 12px rgba(15,23,42,.06);">
                <div style="color:{color};font-size:1.25rem;
                            font-weight:800;">
                    {interpretation['headline']}
                </div>
                <div style="color:#334155;margin-top:5px;">
                    {interpretation['summary']}
                </div>
                <div style="color:#64748B;font-size:.82rem;
                            margin-top:7px;">
                    Confianza: {interpretation['confidence']}
                    · Actualizado: {interpretation['generated_at']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        left,right=st.columns(2)

        with left:
            st.markdown('#### Evidencia Interpretada')
            for item in interpretation['evidence']:
                st.write(f'• {item}')

            if probable_causes:
                st.markdown('#### Causas Probables')
                for item in probable_causes:
                    st.write(f'• {item}')

        with right:
            st.markdown('#### Acciones Recomendadas')
            for index,item in enumerate(
                interpretation['recommendations'],
                1,
            ):
                st.write(f'{index}. {item}')

        if requires_human_review:
            st.warning(
                'Este diagnóstico requiere revisión humana antes '
                'de aplicar cambios.'
            )

        if source == 'IA':
            st.caption(
                'Interpretación generada por IA a partir de '
                'telemetría técnica sanitizada de Condo_Smart.'
            )
            if cache_hit:
                st.caption(
                    'Resultado IA reutilizado desde caché '
                    f'({cache_age:.0f} segundos de antigüedad).'
                )
            else:
                st.caption(
                    'Resultado IA actualizado con la telemetría '
                    'disponible en esta ejecución.'
                )
        elif fallback_reason == 'AGENTE_IA_APAGADO':
            st.caption(
                'Agente IA apagado. Se muestra la interpretación '
                'determinista local.'
            )
        elif fallback_reason == 'IA_NO_CONFIGURADA':
            st.caption(
                'IA todavía no configurada. Se utiliza el motor '
                'determinista local como respaldo seguro.'
            )
        else:
            st.caption(
                'La IA no estuvo disponible. Se utilizó el motor '
                f'local. Motivo técnico: {fallback_reason}'
            )

        if not enabled:
            st.caption(
                'Agente en pausa. La telemetría y el semáforo '
                'continúan funcionando sin actualización automática.'
            )

    _agent_fragment()


def render():
    st.markdown('### Rendimiento Y Observabilidad')
    st.caption('Historial técnico para analizar tiempos de respuesta durante el desarrollo. No almacena datos personales ni valores de formularios.')
    c1,c2,c3=st.columns([1,1,2])
    days=c1.selectbox('Periodo',[1,7,30,90],index=2,key='perf_days')
    module=c2.selectbox('Módulo',['Todos']+modules(),key='perf_module')
    limit=c3.selectbox('Máximo de mediciones',[100,250,500,1000],index=2,key='perf_limit')
    agent_state=bool(
        st.session_state.get('performance_live_agent_enabled', False)
    )
    agent_label=(
        '[ON] Agente en tiempo real'
        if agent_state
        else '[OFF] Agente en tiempo real'
    )
    agent_enabled=st.toggle(
        agent_label,
        value=False,
        key='performance_live_agent_enabled',
        help=(
            'Activa la interpretación IA con refresco visual cada '
            '60 segundos y caché de 5 minutos. La telemetría y el '
            'análisis local continúan aunque esté apagado.'
        ),
    )
    st.caption(
        (
            'ON: refresco cada 60 segundos; la IA se reutiliza '
            'hasta 5 minutos si la telemetría no cambia.'
        )
        if agent_enabled
        else (
            'OFF: agente IA desactivado; la telemetría, el '
            'semáforo y el análisis local continúan.'
        )
    )
    render_live_performance_agent(days,module,limit,agent_enabled)
    snapshot=performance_snapshot(days,module,limit)
    health=snapshot['health']
    color=health['color']
    active={'OPTIMO':(1,0,0),'ATENCION':(0,1,0),'CRITICO':(0,0,1)}.get(health['level'],(0,0,0))
    green_opacity='1' if active[0] else '.18'; yellow_opacity='1' if active[1] else '.18'; red_opacity='1' if active[2] else '.18'
    score_text='--' if health.get('score') is None else f"{health['score']:.1f}/100"
    st.markdown(f"""
    <div style="border:1px solid #D9E2EC;border-radius:18px;padding:20px;background:#FFFFFF;margin:8px 0 18px 0;">
      <div style="display:flex;align-items:center;gap:24px;flex-wrap:wrap;">
        <div style="background:#172033;border-radius:22px;padding:14px 18px;display:flex;gap:12px;box-shadow:0 8px 22px rgba(15,23,42,.16);">
          <div style="width:38px;height:38px;border-radius:50%;background:#16A34A;opacity:{green_opacity};box-shadow:0 0 16px rgba(22,163,74,.45);"></div>
          <div style="width:38px;height:38px;border-radius:50%;background:#F59E0B;opacity:{yellow_opacity};box-shadow:0 0 16px rgba(245,158,11,.45);"></div>
          <div style="width:38px;height:38px;border-radius:50%;background:#DC2626;opacity:{red_opacity};box-shadow:0 0 16px rgba(220,38,38,.45);"></div>
        </div>
        <div style="flex:1;min-width:280px;">
          <div style="font-size:.8rem;color:#64748B;text-transform:uppercase;letter-spacing:.08em;font-weight:700;">Estado actual del rendimiento</div>
          <div style="font-size:2rem;color:{color};font-weight:850;line-height:1.1;">{health['label']}</div>
          <div style="color:#334155;margin-top:6px;">Score {score_text} · Tendencia: {health.get('trend','-')}</div>
          <div style="color:#64748B;font-size:.88rem;margin-top:4px;">Última medición: {health.get('last_recorded_at') or 'Sin datos'}</div>
        </div>
      </div>
    </div>
    """,unsafe_allow_html=True)
    if health['level']=='SIN_DATOS': st.info('Aún no hay datos suficientes para determinar el estado del rendimiento.')
    else:
        h1,h2,h3,h4=st.columns(4)
        h1.metric('Score',score_text)
        h2.metric('P95 reciente',f"{health['recent_p95_ms']:,.1f} ms")
        h3.metric('Errores recientes',f"{health['errors']} ({health['error_rate']:.1f}%)")
        h4.metric('Tendencia',health['trend'],f"{health['delta_pct']:+.1f}%" if health.get('delta_pct') is not None else None)
        with st.expander('¿Por qué aparece este estado?'):
            for reason in health['reasons']: st.write(f'• {reason}')
            st.caption('El semáforo compara las 20 mediciones más recientes con el histórico OK anterior. Cuando no hay al menos 10 muestras históricas, usa temporalmente la referencia optimizada de P95 ≤ 3.000 ms.')
    diagnostic=snapshot['diagnostic']
    layers=diagnostic['layers']
    st.markdown('### Diagnóstico Por Capas')
    st.info(f"Causa dominante estimada: {diagnostic['dominant_cause']}")
    d1,d2,d3,d4=st.columns(4)
    d1.metric('Tiempo total promedio',f"{float(layers.get('total_ms') or 0):,.1f} ms")
    d2.metric('SQL promedio',f"{float(layers.get('sql_ms') or 0):,.1f} ms",f"{diagnostic['sql_pct']:.1f}%")
    d3.metric('Python + render',f"{float(layers.get('app_render_ms') or 0):,.1f} ms",f"{diagnostic['app_render_pct']:.1f}%")
    d4.metric('Consultas promedio',f"{float(layers.get('query_count') or 0):,.1f}")
    if float(layers.get('slowest_query_ms') or 0)>0:
        st.caption(f"Consulta individual más lenta de la ventana reciente: {float(layers['slowest_query_ms']):,.1f} ms")
    else:
        st.warning('Las mediciones históricas anteriores no contienen desglose SQL. Las nuevas mediciones comenzarán a registrar este dato desde ahora.')
    st.markdown('#### Impacto Por Módulo')
    if diagnostic['modules']:
        module_df=pd.DataFrame(diagnostic['modules'])
        st.dataframe(module_df,hide_index=True,use_container_width=True)
        chart_df=module_df[['module','p95_ms']].copy()
        st.bar_chart(chart_df,x='module',y='p95_ms',use_container_width=True)
    else: st.info('No hay datos suficientes para comparar módulos.')
    data=snapshot['summary']
    vals=[('Muestras',int(data.get('total') or 0)),('Promedio',f"{float(data.get('average_ms') or 0):,.1f} ms"),('Mediana',f"{float(data.get('median_ms') or 0):,.1f} ms"),('P95',f"{float(data.get('p95_ms') or 0):,.1f} ms"),('Máximo',f"{float(data.get('max_ms') or 0):,.1f} ms"),('Errores',int(data.get('errors') or 0))]
    for col,(label,value) in zip(st.columns(6),vals): col.metric(label,value)
    trend_rows=snapshot['trends']
    op_rows=snapshot['operations']
    a,b=st.columns(2)
    with a:
        st.markdown('#### Evolución')
        if trend_rows:
            df=pd.DataFrame(trend_rows); st.line_chart(df,x='event_day',y='p95_ms',color='module',use_container_width=True)
        else: st.info('Todavía no hay muestras para el periodo.')
    with b:
        st.markdown('#### Operaciones Más Lentas')
        if op_rows: st.dataframe(pd.DataFrame(op_rows),hide_index=True,use_container_width=True)
        else: st.info('Todavía no hay operaciones registradas.')
    st.markdown('#### Historial De Mediciones')
    rows=snapshot['history']
    if not rows: st.info('El historial comenzará a llenarse al navegar por los módulos.'); return
    display=pd.DataFrame([{'Fecha':r['recorded_at'],'Build':r['build_version'],'Módulo':r['module'],'Operación':r['operation'],'Duración ms':float(r['duration_ms']),'SQL ms':float(r['sql_duration_ms']),'Consultas':r['query_count'],'Estado':r['status']} for r in rows])
    event=st.dataframe(display,hide_index=True,use_container_width=True,on_select='rerun',selection_mode='single-row',key='performance_history_grid')
    selected=list(event.selection.rows or [])
    if selected and 0 <= selected[0] < len(rows):
        row=rows[selected[0]]
        st.markdown('#### Detalle De La Medición Seleccionada')
        st.json({'id':row['id'],'fecha':str(row['recorded_at']),'build':row['build_version'],'modulo':row['module'],'operacion':row['operation'],'duracion_ms':float(row['duration_ms']),'sql_duration_ms':float(row['sql_duration_ms']),'query_count':row['query_count'],'slowest_query_ms':float(row['slowest_query_ms']),'estado':row['status'],'inmueble_id':row['condominio_id'],'metadata':row['metadata_json']})
