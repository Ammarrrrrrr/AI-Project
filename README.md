# 🦁 N-Queens AI Animal Game — Beast Mode Edition

Welcome to the **N-Queens AI Animal Game** — the most advanced, interactive, and fun way to explore the classic N-Queens puzzle! Whether you're a puzzle enthusiast, a student, or just love cute animal icons, this app is for you. Enjoy a beautiful dark mode UI, multi-core AI solving, hints, sound, and endless customization.

---

## 🚀 What is the N-Queens Problem?
The N-Queens problem is a classic chess puzzle: **Place N queens on an N×N chessboard so that no two queens threaten each other.** That means no two queens can share the same row, column, or diagonal.

---

## 🐾 Features
- **Animal Queens:** Choose your favorite animal (🐱 Cat, 🦊 Fox, 🐶 Dog) as the queen icon.
- **Dark Mode UI:** Modern, consistent, and easy on the eyes.
- **Resizable, Responsive Board:** Board grows/shrinks with the window, always centered and square.
- **Multi-core AI Solver:** Blazing fast, parallel N-Queens solving using all your CPU cores.
- **Smart Hints:** Get context-aware hints or suggestions for your next move.
- **Multiple Solutions:** Instantly cycle through all possible solutions for a given board size.
- **Custom Board Colors:** Personalize the board's appearance to your taste.
- **Sound & Animation:** Fun animal sounds and speech bubble feedback.
- **Status Bar:** Real-time feedback and status updates.
- **Beautiful, Accessible Controls:** All controls are easy to use and visually clear.

---

## 🖼️ Screenshots
> _Paste your screenshots here!_

| Main Game | AI Solving | Customization |
|---|---|---|
| ![Main Game](screenshots/main.png) | ![AI Solve](screenshots/ai_solve.png) | ![Customize](screenshots/custom.png) |

---

## 🛠️ Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/Ammarrrrrrr/AI-Project
   cd AI-Project
   ```
2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 📦 Requirements
- Python 3.7+
- PyQt5

---

## 🎮 How to Play
1. **Run the app:**
   ```bash
   python main.py
   ```
2. **Choose your animal:** Click the animal icons at the top right to select your queen.
3. **Set board size:** Use the dropdown to pick any size from 4×4 to 20×20 (except 2 and 3, which have no solutions).
4. **Place queens:** Click on the board to place or remove animal queens. No two queens can attack each other!
5. **Get hints:** Stuck? Click "Hint" for a smart suggestion or to see which queens to move/remove.
6. **AI Solve:** Let the AI instantly solve the puzzle for you using all your CPU cores.
7. **Cycle solutions:** If there are multiple solutions, use the "Show Next Solution" button or the dropdown.
8. **Customize:** Change board colors, reset, or try different animals and board sizes anytime.

---

## 🤖 How the AI Works (Multi-core Power!)
- The AI solver splits the problem across all available CPU cores using Python's `ProcessPoolExecutor`.
- Each process solves for a different starting queen position, then results are combined for maximum speed.
- The UI remains responsive, and you get all solutions as fast as your computer allows!

---

## 🎨 Customization
- **Board Colors:** Click "Change Board Colors" to pick your favorite light/dark square colors.
- **Animal Icons:** Choose between cat, fox, or dog for your queen.
- **Board Size:** Try different N values for new challenges.

---

## 🧩 Project Structure
- `main.py` — Main application and UI logic
- `nqueens_ai.py`, `ai_learning.py` — AI and learning logic (required for full functionality)
- `requirements.txt` — Python dependencies

---

## 🛟 Troubleshooting & FAQ
**Q: The app is slow or freezes on very large boards!**
- A: Solving N-Queens for large N (e.g., 16+) is computationally intensive. The AI uses all your CPU cores, but some sizes may still take time.

**Q: I get a pickling error or multiprocessing error!**
- A: Make sure you're using Python 3.7+ and that all multiprocessing helper functions are defined at the top level of the file.

**Q: The UI looks weird or some widgets are too light!**
- A: Make sure you're using the latest PyQt5 and that your OS theme isn't interfering. All widgets are styled for dark mode.

**Q: I don't hear any sounds!**
- A: Ensure your system audio is on and the required sound files are present in the `assets/` folder.

**Q: Can I add my own animal icons or sounds?**
- A: Yes! Add your PNGs or WAVs to the `assets/` folder and update the code to use them.

---

## 🤝 Contributing
Pull requests and suggestions are welcome! Please open an issue or PR for bug fixes, new features, or improvements.

---

## 🙏 Credits
- Developed by [Your Name or Team]
- Animal icons: [Unicode Emoji]
- Built with [PyQt5](https://riverbankcomputing.com/software/pyqt/)
- Special thanks to the open source community!

---

Enjoy solving N-Queens with a smile — and a roar! 🐱🦊🐶🦁 