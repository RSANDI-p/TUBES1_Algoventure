# Greedy Algorithm Implementation - Algoventure

## 🌟 Overview
The greedy algorithm implemented in this diamond collector bot consistently seeks locally optimal solutions at each decision point. At every turn, the bot selects the most immediately advantageous move - prioritizing the closest diamond based on Manhattan distance, returning to base when inventory is full, or when the base becomes nearer than the next diamond. The algorithm also opportunistically utilizes game features like teleporters when they provide an immediate path optimization, always choosing the option that maximizes short-term gains without considering longer-term collection strategies. This approach exemplifies classic greedy behavior by making the most beneficial local decision at each step while potentially sacrificing global optimization.

## 📦 Prerequisites
Before running, ensure you have:
- [Node.js](https://nodejs.org/) (v14+ recommended)
- Python 3.8+
- [Docker Desktop](https://www.docker.com/products/docker-desktop) (for containerization)
- Yarn package manager
  ```bash
   npm install --global yarn
   ```
- Game Engine

## ⚙️ Installation
1. Download source code (.zip)
2. Extract zip and open the file
3. Go to root directory
  ```bash
  cd tubes1-IF2110-bot-starter-pack-1.0.1
   ```
4. Install dependencies using pip
```
pip install -r requirements.txt
```
5. gunakan venv (jika menggunakan ubuntu)
```
source .venv/bin/activate
```
6. Run bot For 1 bot:
```
python main.py --logic DirectAttack --email=your_email@example.com --name=your_name --password=your_password --team etimo
```
7. Run script in the terminal
```
./run-bots.sh
```

NOTE : email and name in the script must be different each other and never used before


## AUTHOR
1. RIYAN SANDI PRAYOGA
2. Tri Putri Sormin
