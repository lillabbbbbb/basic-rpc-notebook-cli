import xmlrpc.client
from colorama import init, Fore, Style
import shlex
import sys

# Initialize colorama
init(autoreset=True)

#Define some ASI values
ITALIC = '\x1B[3m'
RESET_ITALIC = '\x1B[23m'
BOLD = '\x1B[1m'
RESET_BOLD = '\x1B[22m'

#Connect the client to the server
server = xmlrpc.client.ServerProxy("http://localhost:8000/", allow_none=True)

#Print the menu
def print_guide():
    print(Fore.MAGENTA + "\n--- Notebook RPC CLI Guide ---")
    print(Fore.WHITE + "1. Add notes:")
    print(Fore.YELLOW + ITALIC + "   /add " + ITALIC + Fore.CYAN + "<topic> \"note text\"" + RESET_ITALIC)

    print(Fore.WHITE + "2. View notes by topic or searching text:")
    print(Fore.YELLOW + "   /get " + ITALIC + Fore.CYAN + "<topic>" + RESET_ITALIC)
    print(Fore.YELLOW + ITALIC + "   /get " + ITALIC + Fore.CYAN + "<topic> \"search text\"" + RESET_ITALIC)
    print(Fore.WHITE + "3. Find Wikipedia info:")
    print(Fore.YELLOW + "   /wiki " +  RESET_BOLD + ITALIC + Fore.CYAN + "<topic>" + RESET_ITALIC)

    print(Fore.WHITE + "4. List all topics:")
    print(Fore.YELLOW + "   /list")
    print(Fore.YELLOW + "   /list-detailed")

    print(Fore.WHITE + "5. Help & guide:")
    print(Fore.YELLOW + "   /guide")

    print(Fore.WHITE + "6. Exit:")
    print(Fore.YELLOW + "   /exit\n")
    
    

#Display all topics stored on the server
def list_topics():
    try:
        #first "fetch" the data from the server
        topics = server.list_topics()
        #If there are not topics
        if not topics:
            print(Fore.RED + "No topics found yet.")
            return
        
        #Otherwise display each topic
        for topic, notes in topics.items():
            print(Fore.MAGENTA + topic)
                
    #Handle exceptions
    except Exception as e:
        print(Fore.RED + f"Error fetching topics: {e}")

#Display all topics with all their notes, which are stored on the server
def list_topics_detailed():
    try:
        #first "fetch" the data from the server
        topics = server.list_topics_detailed()
        #If there are no topics
        if not topics:
            print(Fore.RED + "No notes yet.")
            return
        
        #Otherwise display all the topics
        for topic, notes in topics.items():
            print(Fore.MAGENTA + topic)
            for note in notes:
                #And print each note
                print(Fore.CYAN + ITALIC + f"- {note}" + RESET_ITALIC)
            print("")
            
    #Handling exceptions
    except Exception as e:
        print(Fore.RED + f"Error fetching notes: {e}")

#Search across notes and topics
def get_notes(topic, search_text=None):
    try:
        #first "fetch" the data from the server
        if(search_text == None):
            topics = server.get_notes(topic)
        else:
            topics = server.get_notes_search(topic, search_text)
        #If there are no topics
        if not topics:
            print(Fore.RED + "No matches.")
            return
        
        #Otherwise display all the topics
        for topic, notes in topics.items():
            
            if(search_text == None):
                print(Fore.CYAN + topic + Fore.RESET)
            else:
                print(+ topic)
            for note in notes:
                if(search_text):
                    search = search_text.lower()
                    note_lower = note.lower()

                    if search in note_lower:
                        start = note_lower.index(search)
                        end = start + len(search)
                    #And print each note
                    print(Fore.WHITE + ITALIC + f"- {note[:start] + Fore.CYAN + note[start:end] + Fore.WHITE + note[end:]}" + RESET_ITALIC)
                
                else:
                    print(Fore.WHITE + ITALIC + f"- {note}" + RESET_ITALIC)
                
            print("")
            
    #Handling exceptions
    except Exception as e:
        print(Fore.RED + f"Error fetching notes: {e}")


def main():
    print_guide()

    while True:
        try:
            command = input(Fore.BLUE + ">  ").strip()
            if not command:
                continue

            try:
                # Automatically handles multiple quoted strings
                args = shlex.split(command)
            except ValueError as e:
                print(Fore.RED + f"Error parsing command: {e}")
                continue
            
            if not args:
                continue

            cmd = args[0].lower()

            if cmd == "/add" and len(args) >= 3:
                topic = args[1]
                text = args[2]
                result = server.add_note(topic, text)
                print(Fore.GREEN + result)

            elif cmd == "/get" and len(args) >= 2:
                topic = args[1]
                search_text = args[2] if len(args) == 3 else None
                get_notes(topic, search_text)

            elif cmd == "/wiki" and len(args) == 2:
                topic = args[1]
                result = server.get_wiki_info(topic)
                if(result != None):
                    print(Fore.GREEN + result)
                    server.add_note(topic, result)

            elif cmd == "/list":
                list_topics()
                
            elif cmd == "/list-detailed":
                list_topics_detailed()

            elif cmd == "/guide":
                print_guide()

            elif cmd == "/exit":
                print(Fore.MAGENTA + "Exiting client...")
                break

            else:
                print(Fore.RED + "Invalid command. Type '/guide' to see commands.")

        except KeyboardInterrupt:
            print(Fore.MAGENTA + "\nExiting client...")
            sys.exit(0)
        except Exception as e:
            print(Fore.RED + f"Error: {e}")


if __name__ == "__main__":
    main()