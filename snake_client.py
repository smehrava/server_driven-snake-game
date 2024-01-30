import socket
import pygame
import sys
import tkinter as tk

# Setting the games display width and height
pygame.init()
width, height = 500, 500
win = pygame.display.set_mode((width, height))
# Naming the game window: Snake Client
pygame.display.set_caption("Snake Client")

server = "localhost"
port = 5555
# Making a socket for client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Establishing a connection between client and server
    client_socket.connect((server, port))
except socket.error as e:
    # In case any error occurs, this message will be printed
    print(f"Error connecting to server: {e}")
    sys.exit()

# Initialize the score
score = 0


def network_communication(data):
    try:
        # Attempting to send data to the server
        client_socket.sendall(data.encode())
        # Attempting to receive data from server and then decode into string
        received_data = client_socket.recv(4096).decode()
        # If any data was received, return it
        return received_data if received_data else None
    except Exception as e:
        # Handling error
        print(f"Error during network communication: {e}")
        # calling the function handle_disconnection which will terminate the program
        handle_disconnection()


def handle_disconnection():
    # This function will terminate the program in case disconnected from server
    print("Disconnected from server")
    pygame.quit()
    sys.exit()


def draw_game_state(game_state):
    global score  # Use the global score variable

    # if no game state is received call handle_disconnection function
    if game_state is None:
        handle_disconnection()

    # Fill game window with black
    win.fill((0, 0, 0))

    # Draw the grid
    grid_color = (128, 128, 128)  # Gray color for the grid
    block_size = 25  # Set the size of the grid block
    for x in range(0, width, block_size):
        for y in range(0, height, block_size):
            rect = pygame.Rect(x, y, block_size, block_size)
            pygame.draw.rect(win, grid_color, rect, 1)

    try:
        # Parsing the game state received from server
        player_data, snack_data = game_state.split("|")
        player_positions = [eval(pos) for pos in player_data.split("*") if pos]
        snack_positions = [eval(pos) for pos in snack_data.split("**") if pos]

        # Update and draw the score based on the length of the snake
        score = len(player_positions) - 1  # Subtract 1 to not count the head

        # Draw the snake
        for pos in player_positions:
            if isinstance(pos, tuple) and len(pos) == 2:
                # draw each part of a snake as red rectangle
                pygame.draw.rect(win, (255, 0, 0), (pos[0] * block_size, pos[1] * block_size, block_size, block_size))

        # Draw the snacks
        for pos in snack_positions:
            if isinstance(pos, tuple) and len(pos) == 2:
                # draw each snack as green rectangle
                pygame.draw.rect(win, (0, 255, 0), (pos[0] * block_size, pos[1] * block_size, block_size, block_size))

        # Draw the score
        font = pygame.font.SysFont("Arial", 24)
        score_text = font.render("Score: " + str(score), True, (255, 255, 255))
        win.blit(score_text, (5, 5))

        pygame.display.update()

    # Handling Errors
    except SyntaxError as e:
        print(f"Error parsing game state: {e}")
    except TypeError as e:
        print(f"Error drawing game state: {e}")


def show_game_state_popup(game_state):
    # creating a pop of window using tkinter
    popup = tk.Tk()
    popup.title("Current Game State")

    # Use a monospaced font to ensure proper alignment
    state_font = ("Courier", 10)

    # Create a label with the game state text
    label = tk.Label(popup, text=game_state, font=state_font, justify='left')
    label.pack(side="top", fill="both", expand=True, padx=20, pady=20)

    # Create a close button
    close_button = tk.Button(popup, text="Close", command=popup.destroy)
    close_button.pack(pady=10)

    # Position the popup at the center of the screen
    popup_width = 400
    popup_height = 200
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    center_x = int(screen_width / 2 - popup_width / 2)
    center_y = int(screen_height / 2 - popup_height / 2)
    popup.geometry(f'{popup_width}x{popup_height}+{center_x}+{center_y}')

    popup.mainloop()


def show_game_over_popup():
    # creating a pop of window using tkinter
    popup = tk.Tk()
    # Setting the title of window to be "Game Over"
    popup.title("Game Over")

    label = tk.Label(popup, text="Game is over", font=("Arial", 14))
    label.pack(side="top", fill="x", pady=10)

    # Create a close button
    close_button = tk.Button(popup, text="Close", command=lambda: (popup.destroy(), sys.exit()))
    close_button.pack(pady=10)

    # Position the popup at the center of the screen
    popup_width = 200
    popup_height = 100
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    center_x = int(screen_width / 2 - popup_width / 2)
    center_y = int(screen_height / 2 - popup_height / 2)
    popup.geometry(f'{popup_width}x{popup_height}+{center_x}+{center_y}')

    popup.mainloop()


running = True
clock = pygame.time.Clock()

while running:
    clock.tick(10)
    try:
        # Processing all events in the event queue
        for event in pygame.event.get():
            # If the user closes the window, stopping the loop
            if event.type == pygame.QUIT:
                running = False
                network_communication("quit")
                break

            if event.type == pygame.KEYDOWN:
                # If  up arrow is pressed:
                if event.key == pygame.K_UP:
                    network_communication("up")
                # If down arrow is pressed:
                elif event.key == pygame.K_DOWN:
                    network_communication("down")
                # If left arrow is pressed:
                elif event.key == pygame.K_LEFT:
                    network_communication("left")
                # If right arrow is pressed:
                elif event.key == pygame.K_RIGHT:
                    network_communication("right")
                # if 'r' is pressed:
                elif event.key == pygame.K_r:
                    # Sending reset command to the server
                    network_communication("reset")
                    # Resetting the score on the client side
                    score = 0
                # if 'g' is pressed:
                elif event.key == pygame.K_g:
                    # Getting the current game state
                    current_game_state = network_communication("get")
                    # Showing the popup with the game state
                    show_game_state_popup(current_game_state)

                # if 'q' is pressed:
                elif event.key == pygame.K_q:
                    running = False
                    network_communication("quit")
                    show_game_over_popup()
                    break

        # If the game is still running, get the latest game state and update the game display
        if running:
            game_state = network_communication("get")
            draw_game_state(game_state)

    # Handling Exception
    except Exception as e:
        print(f"An error occurred: {e}")
        handle_disconnection()

# Quitting the game when the game is over
pygame.quit()