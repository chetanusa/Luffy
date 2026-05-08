import sys
from pathlib import Path

# Add parent directory to path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

import streamlit as st
import shutil

# Now import from AI.config instead of config
from AI.config.settings import settings
from AI.storage.metadata_store import MetadataStore
from AI.ingest.parsers import DocumentParser
from AI.ingest.preprocessor import DocumentPreprocessor
from AI.extraction.entity_extractor import EntityExtractor
from AI.extraction.relationship_mapper import RelationshipMapper
from AI.graph.builder import GraphBuilder
from AI.ingest.embeddings import EmbeddingGenerator
from AI.storage.vector_store import VectorStore

st.set_page_config(
    page_title="MindWeave - AI Knowledge Graph",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 MindWeave - Personal Knowledge Graph")
st.markdown("---")

# Initialize metadata store
@st.cache_resource
def get_metadata_store():
    return MetadataStore()

metadata_store = get_metadata_store()

# Sidebar
with st.sidebar:
    st.header("📊 Statistics")
    docs = metadata_store.get_all_documents()
    st.metric("Total Documents", len(docs))
    processed = sum(1 for d in docs if d.processed == 1)
    st.metric("Processed", processed)
    st.metric("Pending", len(docs) - processed)
    
    # Show entity and relationship count if any documents processed
    if processed > 0:
        try:
            graph_builder = GraphBuilder()
            entity_count = graph_builder.get_entity_count()
            rel_count = graph_builder.get_relationship_count()
            graph_builder.close()
            st.metric("Total Entities", entity_count)
            st.metric("Total Relationships", rel_count)
        except:
            pass
    
    # Show vector store count
    try:
        vector_store = VectorStore()
        vector_count = vector_store.get_document_count()
        if vector_count > 0:
            st.metric("Indexed for Search", vector_count)
    except:
        pass

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload", "📚 Documents", "🔍 Search", "🧩 Reasoning"])

# Tab 1: Upload
with tab1:
    st.header("Upload Documents")
    st.markdown("Supported formats: PDF, DOCX, MD, TXT")
    
    uploaded_files = st.file_uploader(
        "Choose files",
        type=['pdf', 'docx', 'doc', 'md', 'txt'],
        accept_multiple_files=True
    )
    
    # Add processing options
    col_a, col_b = st.columns(2)
    with col_a:
        extract_entities = st.checkbox("Extract entities (uses AI)", value=True)
    with col_b:
        chunk_size = st.slider("Chunk size", 500, 2000, 1000, 100)
    
    if uploaded_files:
        if st.button("Process Files", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Initialize extractors
            if extract_entities:
                extractor = EntityExtractor()
                rel_mapper = RelationshipMapper()
                graph_builder = GraphBuilder()
                embedding_gen = EmbeddingGenerator()
                vector_store = VectorStore()
            
            for idx, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processing {uploaded_file.name}...")
                
                try:
                    # Save file
                    file_path = settings.UPLOAD_DIR / uploaded_file.name
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Parse document
                    text = DocumentParser.parse_document(str(file_path))
                    
                    # Get preview
                    preview = DocumentParser.get_preview(text, max_length=500)
                    
                    # Save to database
                    doc_id = metadata_store.add_document(
                        title=uploaded_file.name,
                        file_path=str(file_path),
                        file_type=Path(uploaded_file.name).suffix,
                        file_size=uploaded_file.size,
                        content_preview=preview
                    )
                    
                    # Extract entities if enabled
                    if extract_entities:
                        status_text.text(f"🧠 Extracting entities from {uploaded_file.name}...")
                        
                        # Process document
                        processed_doc = DocumentPreprocessor.process_document(text, chunk_size=chunk_size)
                        chunks = processed_doc['chunks']
                        
                        st.info(f"📄 Document split into {len(chunks)} chunks ({processed_doc['total_words']} words)")
                        
                        # Generate embedding for full document
                        status_text.text(f"📊 Generating embeddings for {uploaded_file.name}...")
                        embedding = embedding_gen.generate_embedding(text)
                        
                        if embedding:
                            # Store in vector database
                            vector_store.add_document(doc_id, uploaded_file.name, text, embedding)
                        
                        # Extract entities
                        entities = extractor.batch_extract(chunks)
                        
                        if entities:
                            # Create graph nodes
                            graph_builder.create_entities_batch(entities, doc_id)
                            
                            # Extract relationships
                            status_text.text(f"🔗 Finding relationships in {uploaded_file.name}...")
                            relationships = rel_mapper.batch_extract(chunks, entities)
                            
                            if relationships:
                                # Create relationship edges
                                graph_builder.create_relationships_batch(relationships)
                                st.success(f"✅ {uploaded_file.name}: {len(entities)} entities, {len(relationships)} relationships")
                            else:
                                st.success(f"✅ {uploaded_file.name}: {len(entities)} entities extracted")
                            
                            # Mark as processed
                            metadata_store.mark_processed(doc_id)
                        else:
                            st.warning(f"⚠️ No entities extracted from {uploaded_file.name}")
                    else:
                        st.success(f"✅ {uploaded_file.name} uploaded (ID: {doc_id})")
                    
                except Exception as e:
                    st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
                
                progress_bar.progress((idx + 1) / len(uploaded_files))
            
            if extract_entities:
                total_cost = extractor.get_total_cost() + rel_mapper.get_total_cost() + embedding_gen.get_total_cost()
                st.success(f"💰 Total API cost: ${total_cost:.4f}")
                graph_builder.close()
            
            status_text.text("All files processed!")
            st.balloons()

# Tab 2: Documents
with tab2:
    st.header("Document Library")
    
    docs = metadata_store.get_all_documents()
    
    if not docs:
        st.info("No documents uploaded yet. Go to Upload tab to add documents.")
    else:
        # Display documents
        for doc in docs:
            with st.expander(f"📄 {doc.title}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**ID:** {doc.id}")
                    st.write(f"**Type:** {doc.file_type}")
                    st.write(f"**Size:** {doc.file_size:,} bytes")
                    st.write(f"**Uploaded:** {doc.upload_date.strftime('%Y-%m-%d %H:%M')}")
                
                with col2:
                    status = "✅ Processed" if doc.processed else "⏳ Pending"
                    st.write(f"**Status:** {status}")
                    st.write(f"**Path:** {doc.file_path}")
                
                st.markdown("**Preview:**")
                st.text(doc.content_preview)
                
                # Show entities and relationships if processed
                if doc.processed:
                    st.markdown("**🧠 Extracted Entities:**")
                    try:
                        graph_builder = GraphBuilder()
                        entities = graph_builder.get_document_entities(doc.id)
                        
                        if entities:
                            # Group by type
                            by_type = {}
                            for entity in entities:
                                etype = entity['type']
                                if etype not in by_type:
                                    by_type[etype] = []
                                by_type[etype].append(entity)
                            
                            # Display by type with color coding
                            type_colors = {
                                'PERSON': '👤',
                                'CONCEPT': '💡',
                                'TECHNOLOGY': '⚙️',
                                'ORGANIZATION': '🏢',
                                'TOPIC': '📚'
                            }
                            
                            for etype, ents in by_type.items():
                                icon = type_colors.get(etype, '📌')
                                names = ', '.join([e['name'] for e in ents[:5]])
                                st.markdown(f"{icon} **{etype}:** {names}")
                                if len(ents) > 5:
                                    st.caption(f"... and {len(ents) - 5} more")
                        else:
                            st.info("No entities found")
                        
                        # Show relationships
                        st.markdown("**🔗 Relationships:**")
                        doc_graph = graph_builder.get_document_graph(doc.id)
                        relationships = doc_graph['relationships']
                        
                        if relationships:
                            for rel in relationships[:10]:  # Show first 10
                                if rel['source'] and rel['target']:
                                    st.markdown(f"- **{rel['source']}** → `{rel['type']}` → **{rel['target']}**")
                            if len(relationships) > 10:
                                st.caption(f"... and {len(relationships) - 10} more relationships")
                        else:
                            st.info("No relationships found")
                        
                        graph_builder.close()
                        
                    except Exception as e:
                        st.error(f"Error loading graph data: {str(e)}")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"View Full Content", key=f"view_{doc.id}"):
                        try:
                            text = DocumentParser.parse_document(doc.file_path)
                            st.text_area("Full Content", text, height=300)
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                
                with col_b:
                    if st.button(f"Delete", key=f"delete_{doc.id}", type="secondary"):
                        metadata_store.delete_document(doc.id)
                        st.success(f"Deleted {doc.title}")
                        st.rerun()

# Tab 3: Search
with tab3:
    st.header("🔍 Semantic Search")
    
    # Check if any documents have embeddings
    try:
        vector_store = VectorStore()
        vector_count = vector_store.get_document_count()
        
        if vector_count == 0:
            st.info("📚 No documents with embeddings yet. Upload documents with entity extraction enabled to enable search.")
        else:
            st.success(f"✅ {vector_count} documents indexed for semantic search")
            
            # Search interface
            query = st.text_input(
                "🔎 Search your knowledge base",
                placeholder="e.g., machine learning projects, python development, cloud infrastructure..."
            )
            
            col1, col2 = st.columns([3, 1])
            with col1:
                search_button = st.button("Search", type="primary")
            with col2:
                n_results = st.selectbox("Results", [3, 5, 10], index=1)
            
            if search_button and query:
                with st.spinner("🔍 Searching..."):
                    # Generate query embedding
                    embedding_gen = EmbeddingGenerator()
                    query_embedding = embedding_gen.generate_embedding(query)
                    
                    if query_embedding:
                        # Search vector store
                        results = vector_store.search(query_embedding, n_results=n_results)
                        
                        if results:
                            st.markdown(f"**Found {len(results)} relevant documents:**")
                            
                            for idx, result in enumerate(results):
                                doc = metadata_store.get_document(result['doc_id'])
                                if doc:
                                    similarity_pct = result['similarity'] * 100
                                    
                                    with st.expander(f"#{idx+1} {doc.title} (Similarity: {similarity_pct:.1f}%)"):
                                        st.markdown(f"**Preview:**")
                                        st.text(doc.content_preview)
                                        
                                        if st.button(f"View Full Document", key=f"search_view_{doc.id}"):
                                            try:
                                                full_text = DocumentParser.parse_document(doc.file_path)
                                                st.text_area("Full Content", full_text, height=300)
                                            except Exception as e:
                                                st.error(f"Error: {str(e)}")
                        else:
                            st.warning("No results found. Try a different query.")
                    
                    st.caption(f"💰 Search cost: ${embedding_gen.get_total_cost():.4f}")
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
    
    # Show knowledge graph stats
    st.markdown("---")
    st.markdown("**📊 Knowledge Graph Statistics:**")
    try:
        graph_builder = GraphBuilder()
        entity_count = graph_builder.get_entity_count()
        rel_count = graph_builder.get_relationship_count()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Entities", entity_count)
        with col2:
            st.metric("Relationships", rel_count)
        with col3:
            st.metric("Indexed Documents", vector_count)
        
        graph_builder.close()
    except:
        pass

# Tab 4: Multi-Hop Reasoning
with tab4:
    st.header("🧩 Multi-Hop Reasoning")
    st.markdown("Ask questions that require connecting multiple concepts in your knowledge graph")
    
    try:
        from AI.reasoning.query_engine import GraphQueryEngine
        from AI.reasoning.ai_reasoner import AIReasoner
        
        query_engine = GraphQueryEngine()
        entity_count = query_engine.graph.get_entity_count()
        
        if entity_count < 2:
            st.info("📚 Upload and process at least 2 documents to enable reasoning.")
        else:
            st.success(f"✅ {entity_count} entities in knowledge graph")
            
            # Query type selector
            query_type = st.selectbox(
                "Query Type",
                ["Ask a Question", "Find Path", "Explore Entity", "Find Common Ground"]
            )
            
            if query_type == "Ask a Question":
                st.markdown("**Ask a complex question about your knowledge base:**")
                question = st.text_input(
                    "Question",
                    placeholder="e.g., What technologies does Chetan G work with?"
                )
                
                if st.button("Answer", type="primary"):
                    if question:
                        with st.spinner("🧠 Reasoning..."):
                            reasoner = AIReasoner()
                            
                            # Get answer with automatic context gathering
                            result = reasoner.answer_question(question)
                            
                            st.markdown("**Answer:**")
                            st.write(result['answer'])
                            
                            # Show context used
                            if result.get('context_used', {}).get('entities_found'):
                                with st.expander("🔍 Context Used"):
                                    st.write(f"**Entities found in question:** {', '.join(result['context_used']['entities_found'])}")
                            
                            st.caption(f"💰 Cost: ${result['cost']:.4f}")
                            
                            reasoner.close()
            
            elif query_type == "Find Path":
                st.markdown("**Find connection path between two entities:**")
                
                col1, col2 = st.columns(2)
                with col1:
                    start_entity = st.text_input("Start Entity", placeholder="e.g., Chetan G")
                with col2:
                    end_entity = st.text_input("End Entity", placeholder="e.g., Machine Learning")
                
                max_hops = st.slider("Maximum hops", 1, 5, 3)
                
                if st.button("Find Path", type="primary"):
                    if start_entity and end_entity:
                        with st.spinner("🔍 Finding path..."):
                            path = query_engine.find_path(start_entity, end_entity, max_hops)
                            
                            if path:
                                st.success(f"✅ Found path in {len(path)} hops:")
                                
                                for step in path:
                                    st.markdown(f"**{step['from']}** → `{step['relationship']}` → **{step['to']}**")
                            else:
                                st.warning(f"No path found between {start_entity} and {end_entity} within {max_hops} hops")
            
            elif query_type == "Explore Entity":
                st.markdown("**Explore an entity and its connections:**")
                
                entity_name = st.text_input("Entity Name", placeholder="e.g., Python")
                depth = st.slider("Exploration Depth", 1, 3, 2)
                
                if st.button("Explore", type="primary"):
                    if entity_name:
                        with st.spinner("🔍 Exploring..."):
                            # Get neighbors
                            neighbors = query_engine.get_entity_neighbors(entity_name)
                            
                            if neighbors['outgoing'] or neighbors['incoming']:
                                st.markdown("**Direct Connections:**")
                                
                                if neighbors['outgoing']:
                                    st.markdown("*Outgoing:*")
                                    for conn in neighbors['outgoing']:
                                        st.markdown(f"- **{entity_name}** → `{conn['relationship']}` → {conn['name']} ({conn['type']})")
                                
                                if neighbors['incoming']:
                                    st.markdown("*Incoming:*")
                                    for conn in neighbors['incoming']:
                                        st.markdown(f"- {conn['name']} ({conn['type']}) → `{conn['relationship']}` → **{entity_name}**")
                            else:
                                st.info(f"No connections found for {entity_name}")
                            
                            # Get related entities
                            st.markdown("**Extended Network:**")
                            related = query_engine.find_related_entities(entity_name, depth)
                            
                            if related:
                                for entity in related[:10]:
                                    st.markdown(f"- {entity['name']} ({entity['type']}) - {entity['distance']} hops away")
                            else:
                                st.info("No extended network found")
            
            elif query_type == "Find Common Ground":
                st.markdown("**Find what connects two entities:**")
                
                col1, col2 = st.columns(2)
                with col1:
                    entity1 = st.text_input("First Entity", placeholder="e.g., Python")
                with col2:
                    entity2 = st.text_input("Second Entity", placeholder="e.g., Docker")
                
                if st.button("Find Connections", type="primary"):
                    if entity1 and entity2:
                        with st.spinner("🔍 Finding common ground..."):
                            connections = query_engine.find_common_connections(entity1, entity2)
                            
                            if connections:
                                st.success(f"✅ Found {len(connections)} common connections:")
                                
                                for conn in connections:
                                    st.markdown(f"""
                                    **Bridge: {conn['bridge_entity']}** ({conn['entity_type']})
                                    - {entity1} --[{conn['relationship1']}]--> {conn['bridge_entity']}
                                    - {conn['bridge_entity']} --[{conn['relationship2']}]--> {entity2}
                                    """)
                            else:
                                st.info(f"No direct common connections found. Try 'Find Path' to see if there's an indirect connection.")
        
        query_engine.close()
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

# Footer
st.markdown("---")
st.caption("MindWeave v1.0 - AI-Powered Personal Knowledge Graph")