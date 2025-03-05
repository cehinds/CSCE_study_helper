# CSCE Study Helper

A GUI-based study tool for testing knowledge in various CS topics, including operating systems, process management, scheduling, synchronization, and memory systems. Built with Python/Tkinter.

![Study App Demo](https://github.com/user-attachments/assets/71a798ef-5b9e-4ac1-b60e-3182f2c07824)


## Features

- Load questions from JSON files 
- Multiple question types: MCQs, short answers
- Topic-based quizzes (OS Concepts, Algorithms, Data Structures, etc.)
- Score tracking per topic
- Adjustable settings:
  - Timed questions
  - Attempt limits
  - Text sizing
  - Sound effects
  - UI themes
- Visual feedback for correct/incorrect answers
- Explanation display after attempts
- Image support for questions
![Right](https://github.com/user-attachments/assets/5116480e-e62f-4805-9468-37c25457828c)
![Wrong](https://github.com/user-attachments/assets/a483f360-6ba4-4451-9e04-86bc246e031f)



## Requirements

- Python 3.6+
- Tkinter (usually included with Python)
- Additional libraries:
  ```bash
  pip install pygame Pillow
  ```

## Installation

1. Clone repository:
   ```bash
   git clone https://github.com/cehinds/CSCE_study_helper.git
   cd CSCE_study_helper
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt  # Or install manually:
   pip install pygame Pillow
   ```

3. Download sound files (optional):
   - Place `correct.wav` and `wrong.wav` in root folder for sound effects

## Usage

1. Start the application:
   ```bash
   python midterm_quiz_v0_02.py
   ```

2. Main interface:
   - Left panel: Program description and topic scores
   - Right panel: 
     - Load custom JSON question files
     - Select quiz topics
     - Access settings
     - Quit program

3. Quiz interface:
   - Radio buttons for MCQs
   - Text entry for short answers
   - Attempt counter
   - Next question/Main menu navigation
   - Score display

## Customization

### Question Files
Create JSON files following this structure:
```json
{
    "Subject Title": {
        "description": "Covers process states, PCB, fork/execvp...",
        "questions": [
            {
                "question": "Which state represents a process waiting for I/O?",
                "type": "radio",
                "options": ["Running", "Ready", "Blocked", "New"],
                "answer": "Blocked",
                "explanation": "Blocked state waits for external events...",
                "image": "process_states.png"
            }
        ]
    }
}
```

### Settings
Modify through in-app settings menu:
- Enable/disable timer
- Set maximum attempts (1-5)
- Adjust text size (8-24pt)
- Choose UI theme
- Toggle sound effects
- Enable background music (requires audio files)

## License
GNU GPLv3. See LICENSE file for details.

## Contributing
1. Fork the project
2. Create your feature branch
3. Commit changes
4. Push to the branch
5. Open a PR

Report issues for any bugs or feature requests.

## Acknowledgment
This project utilized AI assistance, including DeepSeek R1 and ChatGPT-4o, for drafting and refinement in accordance with IEEE guidelines.

