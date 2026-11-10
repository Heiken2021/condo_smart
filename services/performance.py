from datetime import datetime
import json
import time
import uuid
from contextlib import ContextDecorator
import streamlit as st
from core.config import BUILD
from core.db import execute, fetch_all, fetch_one, reset_query_stats, query_stats


def session_key():
    if 'performance_session_key' not in st.session_state:
        st.session_state.performance_session_key=uuid.uuid4().hex[:24]
    return st.session_state.performance_session_key


def record_event(module,operation,duration_ms,status='OK',property_id=None,metadata=None,sql_duration_ms=0,query_count=0,slowest_query_ms=0):
    try:
        execute("""INSERT INTO performance_events(build_version,session_key,module,operation,duration_ms,sql_duration_ms,query_count,slowest_query_ms,status,condominio_id,metadata_json) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)""",
          (BUILD,session_key(),module,operation,float(duration_ms),float(sql_duration_ms),int(query_count),float(slowest_query_ms),status,property_id,json.dumps(metadata or {},ensure_ascii=False)))
    except Exception:
        pass


class measure(ContextDecorator):
    def __init__(self,module,operation,property_id=None,metadata=None):
        self.module=module; self.operation=operation; self.property_id=property_id; self.metadata=metadata or {}
    def __enter__(self):
        reset_query_stats()
        self.started=time.perf_counter(); return self
    def __exit__(self,exc_type,exc,tb):
        elapsed=(time.perf_counter()-self.started)*1000
        stats=query_stats()
        render_ms=max(0.0,elapsed-float(stats["duration_ms"]))
        metadata={
            **self.metadata,
            "python_render_ms":round(render_ms,3),
            "sql_share_pct":round(
                (
                    float(stats["duration_ms"])
                    / elapsed
                    * 100
                )
                if elapsed
                else 0,
                2,
            ),
        }

        if exc_type is None:
            status='OK'
        elif exc_type.__name__ == 'RerunException':
            status='RERUN'
        else:
            status='ERROR'

        if exc_type is not None:
            metadata["exception_type"]=exc_type.__name__

        record_event(
            self.module,
            self.operation,
            elapsed,
            status,
            self.property_id,
            metadata,
            stats["duration_ms"],
            stats["count"],
            stats["slowest_ms"],
        )

        return False


def summary(days=30,module=None):
    params=[days]
    where="recorded_at >= NOW()-(%s * INTERVAL '1 day')"
    if module and module!='Todos': where+=' AND module=%s'; params.append(module)
    return fetch_one(f"""SELECT COUNT(*) total,COALESCE(AVG(duration_ms),0) average_ms,COALESCE(PERCENTILE_CONT(.5) WITHIN GROUP(ORDER BY duration_ms),0) median_ms,COALESCE(PERCENTILE_CONT(.95) WITHIN GROUP(ORDER BY duration_ms),0) p95_ms,COALESCE(MAX(duration_ms),0) max_ms,COUNT(*) FILTER(WHERE status='ERROR') errors,COALESCE(SUM(query_count),0) queries FROM performance_events WHERE {where}""",tuple(params))


def modules():
    return [r['module'] for r in fetch_all('SELECT DISTINCT module FROM performance_events ORDER BY module')]


def history(days=30,module=None,limit=500):
    params=[days]
    where="recorded_at >= NOW()-(%s * INTERVAL '1 day')"
    if module and module!='Todos': where+=' AND module=%s'; params.append(module)
    params.append(limit)
    return fetch_all(f"""SELECT id,recorded_at,build_version,module,operation,duration_ms,sql_duration_ms,query_count,slowest_query_ms,status,condominio_id,metadata_json FROM performance_events WHERE {where} ORDER BY recorded_at DESC LIMIT %s""",tuple(params))


def trends(days=30,module=None):
    params=[days]
    where="recorded_at >= NOW()-(%s * INTERVAL '1 day')"
    if module and module!='Todos': where+=' AND module=%s'; params.append(module)
    return fetch_all(f"""SELECT DATE(recorded_at) AS event_day,module,ROUND(AVG(duration_ms),2) AS average_ms,ROUND(PERCENTILE_CONT(.95) WITHIN GROUP(ORDER BY duration_ms)::numeric,2) AS p95_ms,COUNT(*) AS samples FROM performance_events WHERE {where} GROUP BY DATE(recorded_at),module ORDER BY event_day,module""",tuple(params))


def by_operation(days=30,module=None):
    params=[days]
    where="recorded_at >= NOW()-(%s * INTERVAL '1 day')"
    if module and module!='Todos': where+=' AND module=%s'; params.append(module)
    return fetch_all(f"""SELECT module,operation,COUNT(*) samples,ROUND(AVG(duration_ms),2) average_ms,ROUND(PERCENTILE_CONT(.95) WITHIN GROUP(ORDER BY duration_ms)::numeric,2) p95_ms,MAX(duration_ms) max_ms,COUNT(*) FILTER(WHERE status='ERROR') errors FROM performance_events WHERE {where} GROUP BY module,operation ORDER BY p95_ms DESC""",tuple(params))


def performance_health(days=30,module=None,recent_limit=20):
    """Calcula salud relativa: la referencia es el histórico OK anterior a la ventana reciente."""
    params=[days]
    where="recorded_at >= NOW()-(%s * INTERVAL '1 day')"
    if module and module!='Todos':
        where+=' AND module=%s'; params.append(module)
    params.append(recent_limit)
    recent=fetch_one(f"""WITH recent AS (
        SELECT duration_ms,status,recorded_at
        FROM performance_events WHERE {where}
        ORDER BY recorded_at DESC LIMIT %s
    )
    SELECT COUNT(*) total,
           COALESCE(AVG(duration_ms),0) average_ms,
           COALESCE(PERCENTILE_CONT(.95) WITHIN GROUP(ORDER BY duration_ms),0) p95_ms,
           COUNT(*) FILTER(WHERE status='ERROR') errors,
           MAX(recorded_at) last_recorded_at
    FROM recent""",tuple(params))
    total=int(recent.get('total') or 0)
    if not total:
        return {'level':'SIN_DATOS','label':'Datos insuficientes','score':None,'color':'#94A3B8','recent_total':0,'reasons':['Todavía no existen mediciones para evaluar.']}

    history_params=[days]
    history_where="recorded_at >= NOW()-(%s * INTERVAL '1 day')"
    if module and module!='Todos':
        history_where+=' AND module=%s'; history_params.append(module)
    history_params.append(recent_limit)
    baseline=fetch_one(f"""WITH ordered AS (
        SELECT duration_ms,status,recorded_at,
               ROW_NUMBER() OVER(ORDER BY recorded_at DESC) rn
        FROM performance_events WHERE {history_where}
    )
    SELECT COUNT(*) total,
           COALESCE(AVG(duration_ms) FILTER(WHERE status='OK'),0) average_ms,
           COALESCE(PERCENTILE_CONT(.95) WITHIN GROUP(ORDER BY duration_ms) FILTER(WHERE status='OK'),0) p95_ms,
           COUNT(*) FILTER(WHERE status='ERROR') errors
    FROM ordered WHERE rn>%s""",tuple(history_params))

    recent_avg=float(recent.get('average_ms') or 0); recent_p95=float(recent.get('p95_ms') or 0)
    errors=int(recent.get('errors') or 0); error_rate=errors/total if total else 0
    baseline_total=int(baseline.get('total') or 0); baseline_p95=float(baseline.get('p95_ms') or 0)
    # Si aún no hay referencia suficiente, se usa el objetivo optimizado de 2 s y P95 de 3 s.
    reference_p95=baseline_p95 if baseline_total>=10 and baseline_p95>0 else 3000.0
    ratio=recent_p95/reference_p95 if reference_p95 else 1.0
    score=100.0
    score-=min(55.0,max(0.0,(ratio-0.75)*55.0/0.75))
    score-=min(40.0,error_rate*200.0)
    score=round(max(0.0,min(100.0,score)),1)
    if error_rate>=0.20 or ratio>=1.75 or score<50:
        level,label,color='CRITICO','Crítico','#DC2626'
    elif error_rate>=0.05 or ratio>=1.15 or score<75:
        level,label,color='ATENCION','Atención','#F59E0B'
    else:
        level,label,color='OPTIMO','Óptimo','#16A34A'
    if baseline_total>=10:
        delta=((recent_p95-baseline_p95)/baseline_p95*100) if baseline_p95 else 0
        trend='Mejora' if delta<=-10 else ('Degradación' if delta>=10 else 'Estable')
        reference_text=f'P95 histórico de referencia: {baseline_p95:,.1f} ms.'
    else:
        delta=None; trend='Sin referencia histórica suficiente'; reference_text='Referencia provisional optimizada: P95 de 3.000 ms.'
    reasons=[f'P95 reciente: {recent_p95:,.1f} ms.',f'Promedio reciente: {recent_avg:,.1f} ms.',f'Errores recientes: {errors} de {total}.',reference_text]
    return {'level':level,'label':label,'score':score,'color':color,'recent_total':total,
            'recent_average_ms':recent_avg,'recent_p95_ms':recent_p95,'errors':errors,
            'error_rate':round(error_rate*100,1),'baseline_total':baseline_total,
            'baseline_p95_ms':baseline_p95,'ratio':round(ratio,3),'trend':trend,
            'delta_pct':round(delta,1) if delta is not None else None,
            'last_recorded_at':recent.get('last_recorded_at'),'reasons':reasons}


def diagnostic_breakdown(days=30,module=None,recent_limit=20):
    params=[days]
    where="recorded_at >= NOW()-(%s * INTERVAL '1 day')"
    if module and module!='Todos': where+=' AND module=%s'; params.append(module)
    params.append(recent_limit)
    layers=fetch_one(f"""WITH recent AS (
        SELECT * FROM performance_events WHERE {where} ORDER BY recorded_at DESC LIMIT %s
    ) SELECT COUNT(*) samples,COALESCE(AVG(duration_ms),0) total_ms,
             COALESCE(AVG(sql_duration_ms),0) sql_ms,
             COALESCE(AVG(GREATEST(duration_ms-sql_duration_ms,0)),0) app_render_ms,
             COALESCE(AVG(query_count),0) query_count,
             COALESCE(MAX(slowest_query_ms),0) slowest_query_ms
      FROM recent""",tuple(params))
    module_params=[days]
    module_where="recorded_at >= NOW()-(%s * INTERVAL '1 day')"
    if module and module!='Todos': module_where+=' AND module=%s'; module_params.append(module)
    modules_rows=fetch_all(f"""SELECT module,COUNT(*) samples,ROUND(AVG(duration_ms),1) average_ms,
        ROUND(PERCENTILE_CONT(.95) WITHIN GROUP(ORDER BY duration_ms)::numeric,1) p95_ms,
        ROUND(AVG(sql_duration_ms),1) sql_ms,
        ROUND(AVG(GREATEST(duration_ms-sql_duration_ms,0)),1) app_render_ms,
        COUNT(*) FILTER(WHERE status='ERROR') errors
        FROM performance_events WHERE {module_where} GROUP BY module ORDER BY p95_ms DESC""",tuple(module_params))
    total=float(layers.get('total_ms') or 0); sql=float(layers.get('sql_ms') or 0); app=float(layers.get('app_render_ms') or 0)
    if int(layers.get('samples') or 0)==0: cause='Sin datos suficientes'
    elif sql>app: cause='Base de datos / SQL'
    else: cause='Lógica Python y renderizado Streamlit'
    return {'layers':dict(layers),'modules':modules_rows,'dominant_cause':cause,
            'sql_pct':round(sql/total*100,1) if total else 0,'app_render_pct':round(app/total*100,1) if total else 0}


def performance_agent_interpretation(days=30,module=None,snapshot=None):
    """Agente determinista: interpreta telemetria local sin enviar datos a servicios externos."""
    snapshot=snapshot or performance_snapshot(days,module,500)
    health=snapshot['health']
    diagnostic=snapshot['diagnostic']
    operations=snapshot['operations']
    modules_ranked=diagnostic.get('modules') or []
    evidence=[]; recommendations=[]
    if health.get('level')=='SIN_DATOS':
        return {'headline':'Aún no hay datos suficientes','summary':'Navega por la aplicación para generar una ventana representativa.','evidence':health.get('reasons',[]),'recommendations':['Generar al menos 20 mediciones recientes antes de tomar decisiones.'],'confidence':'Baja','generated_at':datetime.now().astimezone(),'level':'SIN_DATOS'}
    p95=float(health.get('recent_p95_ms') or 0); error_rate=float(health.get('error_rate') or 0)
    cause=diagnostic.get('dominant_cause') or 'Sin causa dominante'
    sql_pct=float(diagnostic.get('sql_pct') or 0); app_pct=float(diagnostic.get('app_render_pct') or 0)
    evidence.extend([f"P95 reciente: {p95:,.1f} ms.",f"Tasa de errores reciente: {error_rate:.1f}%.",f"Capa dominante estimada: {cause} ({max(sql_pct,app_pct):.1f}% del tiempo promedio)."])
    if modules_ranked:
        worst=modules_ranked[0]
        evidence.append(f"Módulo de mayor impacto: {worst['module']} con P95 de {float(worst['p95_ms']):,.1f} ms y {int(worst['errors'])} errores.")
    if operations:
        slow=operations[0]
        evidence.append(f"Operación más lenta: {slow['module']} / {slow['operation']} con P95 de {float(slow['p95_ms']):,.1f} ms.")
    if error_rate>=20: recommendations.append('Prioridad inmediata: revisar primero las excepciones recientes; los errores distorsionan el tiempo y la experiencia del usuario.')
    elif error_rate>=5: recommendations.append('Revisar los errores recientes antes de ajustar umbrales de rendimiento.')
    if sql_pct>=50:
        recommendations.extend(['Analizar las consultas del módulo de mayor impacto y sus planes de ejecución.','Revisar índices, cardinalidad, consultas repetidas y la consulta individual más lenta.'])
    else:
        recommendations.extend(['Priorizar reruns, construcción repetida de componentes, carga de datos duplicada y trabajo Python durante el render.','Aplicar caché sólo a lecturas estables y dividir paneles costosos con fragmentos independientes.'])
    if p95>3000: recommendations.append('Mantener el estado fuera de verde hasta sostener un P95 inferior a 3.000 ms en varias ventanas consecutivas.')
    if health.get('trend')=='Degradación': recommendations.append('Comparar los cambios recientes y el módulo de mayor impacto contra la última referencia optimizada.')
    headline={'OPTIMO':'Rendimiento estable dentro de la referencia','ATENCION':'Se detecta degradación que requiere seguimiento','CRITICO':'Intervención recomendada antes de consolidar producción'}.get(health.get('level'),'Estado no determinado')
    summary=f"El agente clasifica el estado como {health.get('label')}. La causa dominante estimada es {cause}."
    confidence='Alta' if int(health.get('recent_total') or 0)>=20 and int(health.get('baseline_total') or 0)>=10 else 'Media'
    return {'headline':headline,'summary':summary,'evidence':evidence,'recommendations':recommendations[:5],'confidence':confidence,'generated_at':datetime.now().astimezone(),'level':health.get('level')}


@st.cache_data(ttl=30,show_spinner=False,max_entries=64)
def performance_snapshot(days=30,module=None,limit=500):
    """Instantanea unica compartida por agente, semaforo, diagnostico y graficas."""
    return {
        'health':performance_health(days,module),
        'diagnostic':diagnostic_breakdown(days,module),
        'operations':by_operation(days,module),
        'summary':summary(days,module),
        'trends':trends(days,module),
        'history':history(days,module,limit),
        'modules':modules(),
        'generated_at':datetime.now().astimezone(),
    }


def clear_performance_cache():
    performance_snapshot.clear()
