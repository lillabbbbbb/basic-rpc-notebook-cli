import xmlrpc.server
from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn
import xml.etree.ElementTree as ET
from datetime import datetime
import threading
import requests
from colorama import init, Fore, Style

#Thread lock for safe concurrent access
LOCK = threading.Lock()

#Define the database file
XML_FILE = "notebook.xml"

#Make sure XML file xists
try:
    tree = ET.parse(XML_FILE)
    root = tree.getroot()
except FileNotFoundError:
    root = ET.Element("notebook")
    tree = ET.ElementTree(root)
    tree.write(XML_FILE)

#Fetch link to topic from wikipedia
def get_wikipedia_info(topic):
    url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={topic}&format=json" #request to the correct API endpoint
    headers={"User-Agent": "NotebookRPC/1.0 (https://example.com)"} #this is required for Wikipedia to serve the request
    try:
        response = requests.get(url, headers=headers, timeout=5)
        requests.get(url, headers=headers, timeout=5).raise_for_status()
        response = response.json()
        print(response)
        
        #if response is valid
        if response[1]:
            title = response[1][0]
            link = response[3][0]
            return f"Link to {title}: {link}"
        
    #Handle exceptions
    except Exception as e:
        print(f"Error fetching Wikipedia for topic '{topic}': {e}")
        return None


#Threaded XML-RPC server
class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

#Notebook server
class NotebookServer:

    #Add note to topic
    def add_note(self, topic, text, timestamp=None):
        
        #add timestamp
        if timestamp is None:
            timestamp = datetime.now().isoformat()
            
        with LOCK:
            tree = ET.parse(XML_FILE)
            root = tree.getroot()
            
            #search for existing topic with this name
            topic_elem = root.find(f"./topic[@name='{topic}']")
            
            #if the topic doesn't exist yet
            if topic_elem is None:
                topic_elem = ET.SubElement(root, "topic", {"name": topic})
                
            #check if there is an identical note in this topic already
            for note in topic_elem.findall("note"):
                if note.text and note.text.strip() == text.strip():
                    return f"This note already exists under topic '{topic}'"

            note_elem = ET.SubElement(topic_elem, "note", {"timestamp": timestamp})
            note_elem.text = text
            
            #save changes to xml file
            tree.write(XML_FILE)
                
        return f"Note added under topic '{topic}'"

    # Get all notes for a topic
    def get_notes(self, topic):
        with LOCK:
            tree = ET.parse(XML_FILE)
            root = tree.getroot()
            result = {}
            
            if(topic == "*"):
                for topic_elem in root.findall("topic"):
                    topic_name = topic_elem.get("name")
                    notes = [note.text +  f" [{note.get("timestamp")}]" for note in topic_elem.findall("note")]
                    result[topic_name] = notes
                return result
            topic_elem = root.find(f"./topic[@name='{topic}']")
            
            if topic_elem is None:
                return []
            
            topic_name = topic_elem.get("name")
            notes = [note.text +  f" [{note.get("timestamp")}]" for note in topic_elem.findall("note")]
            result[topic_name] = notes
            return result

    #get notes for a topic filtered by search text
    def get_notes_search(self, topic, search_text):
        with LOCK:
            tree = ET.parse(XML_FILE)
            root = tree.getroot()
            
            topic_elem = None
            if(topic != "*"):
                topic_elem = root.find(f"./topic[@name='{topic}']")
                if topic_elem is None:
                    return []
                
            result = {}
            for topic_elem in root.findall("topic"):
                topic_name = topic_elem.get("name")
                notes = []
                for note in topic_elem.findall("note"):
                    if(search_text.lower() in note.text.lower()):

                        notes.append(note.text + f" [{note.get("timestamp")}]")
                            
                if(notes != []):
                    result[topic_name] = notes
        
            return result

    #list all topics (just the topic names)
    def list_topics(self):
        with LOCK:
            tree = ET.parse(XML_FILE)
            root = tree.getroot()
            return {topic.get("name"): [] for topic in root.findall("topic")}

    #list all topics with their notes
    def list_topics_detailed(self):
        with LOCK:
            tree = ET.parse(XML_FILE)
            root = tree.getroot()
            result = {}
            for topic_elem in root.findall("topic"):
                topic_name = topic_elem.get("name")
                notes = [note.text + f" [{note.get("timestamp")}]" for note in topic_elem.findall("note")]
                result[topic_name] = notes
            return result

    def get_wiki_info(self, topic):
        if(topic == None):
            return
        
        return get_wikipedia_info(topic)

#Running the server
if __name__ == "__main__":
    server = ThreadedXMLRPCServer(("localhost", 8000), allow_none=True) #configure the threaded server with domain and port
    server.register_instance(NotebookServer())
    print(Fore.MAGENTA + "\n--- Notebook RPC Server Started ---")
    print(Fore.WHITE + "Listening on port 8000...")
    server.serve_forever()