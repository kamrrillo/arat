import streamlit as st
from neo4j import GraphDatabase
from streamlit_agraph import agraph, Node, Edge, Config
import os

st.set_page_config(layout="wide", page_title="ARAT Visualizer")

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

@st.cache_resource
def get_driver():
    return GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def get_graph_data(limit=50):
    driver = get_driver()
    nodes = []
    edges = []
    node_ids = set()
    
    query = """
    MATCH (a:Alumno)-[r:INSCRITO_EN]->(g:Grupo)
    RETURN a.id AS alumno_id, a.carrera AS carrera, g.id AS grupo_id, g.asignatura AS asignatura
    LIMIT $limit
    """
    
    with driver.session() as session:
        result = session.run(query, limit=limit)
        
        for record in result:
            a_id = record["alumno_id"]
            g_id = record["grupo_id"]
            
            # Nodo Alumno
            if a_id not in node_ids:
                nodes.append(Node(
                    id=a_id, 
                    label="Estudiante", 
                    size=15, 
                    color="#FF6B6B",
                    title=f"Carrera: {record['carrera']}" 
                ))
                node_ids.add(a_id)
            
            # Nodo Grupo
            if g_id not in node_ids:
                nodes.append(Node(
                    id=g_id, 
                    label=record["asignatura"],
                    size=20, 
                    color="#4D96FF"
                ))
                node_ids.add(g_id)
            
            # Relación
            edges.append(Edge(
                source=a_id, 
                target=g_id, 
                label="CURSA"
            ))
            
    return nodes, edges

# --- INTERFAZ WEB ---
st.title("ARAT")
st.markdown("Vista anonimizada de relaciones Académicas.")

# Sidebar de filtros
limit = st.sidebar.slider("Cantidad de relaciones a mostrar", 10, 500, 50)

# Cargar Grafo
with st.spinner("Cargando grafo desde Neo4j..."):
    nodes, edges = get_graph_data(limit)

config = Config(width="100%", height=600, directed=True, nodeHighlightBehavior=True, highlightColor="#F7A7A6", collapsible=False)

# Renderizar
if nodes:
    agraph(nodes=nodes, edges=edges, config=config)
else:
    st.warning("No se encontraron datos. ¿Ya ejecutaste el script de ingesta?")

st.sidebar.info(f"Nodos visualizados: {len(nodes)}")
