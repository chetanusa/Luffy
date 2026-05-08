from ingest.parsers import DocumentParser
from ingest.preprocessor import DocumentPreprocessor
from storage.metadata_store import MetadataStore

def test_txt_parser():
    """Test TXT parsing"""
    # Create a test file
    test_file = "test.txt"
    with open(test_file, 'w') as f:
        f.write("This is a test document.\nIt has multiple lines.\nFor testing purposes.")
    
    text = DocumentParser.parse_txt(test_file)
    assert "test document" in text
    print("✅ TXT parser works")
    
    # Cleanup
    import os
    os.remove(test_file)

def test_preprocessor():
    """Test text preprocessing"""
    text = "This   is  a    test.   With   extra   spaces!"
    cleaned = DocumentPreprocessor.clean_text(text)
    assert "  " not in cleaned
    print("✅ Preprocessor works")

def test_metadata_store():
    """Test database operations"""
    store = MetadataStore()
    
    # Add document
    doc_id = store.add_document(
        title="Test Doc",
        file_path="/tmp/test.txt",
        file_type=".txt",
        file_size=100,
        content_preview="This is a test"
    )
    
    # Retrieve document
    doc = store.get_document(doc_id)
    assert doc.title == "Test Doc"
    
    # Delete document
    store.delete_document(doc_id)
    
    store.close()
    print("✅ Metadata store works")

if __name__ == "__main__":
    test_txt_parser()
    test_preprocessor()
    test_metadata_store()
    print("\n🎉 All parser tests passed!")