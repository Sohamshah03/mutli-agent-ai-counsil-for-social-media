# 🤖 AI Marketing Council

> **Autonomous Multi-Agent System for Social Media Strategy & Content Generation**

An agentic AI system that replicates a professional marketing team through debate-driven decision making. Unlike static tools, this council of specialized AI agents negotiates conflicting objectives (Virality vs Brand Safety) to produce, optimize, and learn from social media campaigns autonomously.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)

---

## 🎯 Project Overview

### The Challenge

Design a **fully autonomous multi-agent AI council** that:
- ✅ Operates as a self-correcting ecosystem with persistent memory
- ✅ Executes "Observe-Debate-Act-Learn" cycles
- ✅ Resolves strategic conflicts without human intervention
- ✅ Adapts dynamically to real-time trends and feedback

### Our Solution

A **5-agent debate system** where:
1. **Viral Hunter** pushes for maximum engagement
2. **Brand Guardian** protects reputation and consistency
3. **Twitter/X Specialist** optimizes for platform-specific virality
4. **Instagram Specialist** focuses on visual storytelling
5. **Arbitrator** makes weighted final decisions based on past performance

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUT LAYER                              │
│  Brand Context • Product Info • Target Audience • Trends    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  DEBATE ENGINE                              │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Viral   │  │  Brand   │  │ Twitter  │  │Instagram │   │
│  │  Hunter  │  │ Guardian │  │Specialist│  │Specialist│   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│       ↓             ↓             ↓             ↓          │
│  Propose Ideas → Critique Each Other → Debate              │
│                                                             │
│                  ┌──────────────┐                          │
│                  │  Arbitrator  │                          │
│                  │ (Weighted    │                          │
│                  │  Decisions)  │                          │
│                  └──────────────┘                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│               CONTENT GENERATION                            │
│  Platform-Optimized Text • AI-Generated Images              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                LEARNING LOOP                                │
│  Engagement Simulation → Performance Analysis →             │
│  Agent Weight Updates → Strategy Drift                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- API Keys (all free):
  - [Groq](https://console.groq.com/) - Free, unlimited LLM access
  - [HuggingFace](https://huggingface.co/settings/tokens) - Free image generation
  - [Reddit](https://www.reddit.com/prefs/apps) - Free trends API

### Installation

```bash
# Clone the repository
git clone https://github.com/Captain-MUDIT/mutli-agent-ai-counsil-for-social-media
cd ai-marketing-council

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Configure API Keys

Edit `.env` file:

```bash
# Required
GROQ_API_KEY=your_groq_api_key_here
HUGGINGFACE_TOKEN=your_huggingface_token_here

# Optional (for real-time trends)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=AIMarketingCouncil/1.0
```

### Run the Application

```bash
# Start Streamlit dashboard
streamlit run app.py

# Or run command-line version
python -m src.debate
```

---

## 📖 Usage Guide

### Dashboard Navigation

1. **Input Tab** - Configure campaign parameters
   - Enter brand name and industry
   - Describe your product/campaign
   - Define target audience
   - Toggle real-time trends and image generation

2. **Debate Tab** - Watch agents argue in real-time
   - View trending topics
   - Read agent proposals
   - See critique exchanges
   - Understand arbitrator's decision

3. **Content Tab** - Review generated posts
   - Platform-optimized captions
   - AI-generated images
   - Hashtag recommendations
   - Posting time suggestions

4. **Analytics Tab** - Track learning over time
   - Agent weight evolution
   - Engagement performance
   - Winner distribution

5. **Comparison Tab** - Compare iterations
   - Before/after learning
   - Strategy drift analysis
   - Performance improvements

### Example Campaign

```python
from src.debate import DebateOrchestrator

# Initialize system
orchestrator = DebateOrchestrator()

# Define campaign
context = {
    "brand_name": "TechFlow AI",
    "industry": "Technology / SaaS",
    "product_info": "Smart Scheduling Assistant - AI calendar optimization",
    "target_audience": "Busy professionals, startup founders"
}

# Run campaign iteration
result = orchestrator.run_campaign_iteration(
    context,
    use_api_trends=True,
    generate_image=True
)

# Access results
print(f"Winner: {result['decision']['winner']}")
print(f"Engagement Score: {result['engagement']['overall_score']}/10")
print(f"Caption: {result['content']['caption']}")
```

---

## 🧠 How It Works

### 1. Trend Intelligence

```python
# Fetches from multiple sources
- Google Trends: Real-time search trends
- Reddit API: Hot topics from r/technology, r/startups
- Fallback: Curated sample trends
```

### 2. Agent Debate Process

**Round 1: Proposals**
- Each agent proposes 2-3 campaign ideas
- Specifies platform, content approach, and reasoning
- Rates ideas from their perspective (1-10)

**Round 2: Critiques**
- Agents critique each other's proposals
- Identify conflicts with their goals
- Point out risks and missed opportunities

**Round 3: Arbitration**
- Arbitrator weighs all arguments
- Applies voting weights based on past performance
- Makes final decision with detailed reasoning

### 3. Content Generation

```python
# Platform-specific optimization
Twitter: 280 chars, punchy, 2 hashtags
Instagram: 2200 chars, visual-first, 8 hashtags
LinkedIn: 3000 chars, professional, 4 hashtags

# Multimodal output
- Text: Groq Llama 3.1 70B
- Images: HuggingFace Stable Diffusion XL
```

### 4. Learning Mechanism

```python
# Performance-based weight adjustment
if agent.won and performance > 7/10:
    agent.weight += 0.2  # Boost influence
elif agent.lost:
    agent.weight -= 0.1  # Reduce influence

# Strategy drift over iterations
Iteration 1: Viral wins (high engagement)
Iteration 2: Viral's weight increased
Result: More aggressive strategies favored
```

---

## 📊 Key Features

### ✅ Core Requirements Met

| Requirement | Implementation | Status |
|------------|---------------|---------|
| Multi-Agent Conflict | 5 agents with opposing goals | ✅ |
| Debate-Driven | Proposal → Critique → Arbitration | ✅ |
| Trend Intelligence | Google + Reddit + Fallback | ✅ |
| Multimodal Generation | Text (Groq) + Images (HF) | ✅ |
| Closed-Loop Learning | Weight adjustment based on performance | ✅ |
| Strategy Transparency | Full debate logs + reasoning traces | ✅ |
| Persistent Memory | JSON-based agent weight history | ✅ |

### 🎨 Unique Differentiators

1. **Real Conflict Resolution** - Agents genuinely disagree and negotiate
2. **Observable Learning** - Watch strategy shift across iterations
3. **Transparent Reasoning** - Every decision fully explained
4. **Platform Specialization** - Experts for Twitter, Instagram, LinkedIn
5. **No Human Intervention** - Fully autonomous decision making

---

## 🗂️ Project Structure

```
ai-marketing-council/
├── config/
│   └── agents.json              # Agent configurations & personalities
├── data/
│   └── sample_trends.json       # Fallback trending topics
├── src/
│   ├── agents.py               # Agent classes & debate logic
│   ├── trends.py               # Trend fetching (Google/Reddit)
│   ├── content_gen.py          # Text & image generation
│   └── debate.py               # Orchestration & learning loop
├── outputs/
│   ├── generated_images/       # AI-generated post images
│   └── debate_logs/            # JSON logs of each iteration
├── app.py                      # Streamlit dashboard
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
└── README.md                  # This file
```

---

## 🔧 Configuration

### Agent Personalities

Edit `config/agents.json` to customize agent behavior:

```json
{
  "viral_hunter": {
    "personality": "Aggressive, trend-focused, risk-taking",
    "goals": [
      "Maximize likes and shares",
      "Leverage viral formats",
      "Prioritize reach over safety"
    ],
    "voting_weight": 1.0
  }
}
```

### Platform Settings

```json
{
  "twitter": {
    "char_limit": 280,
    "optimal_hashtags": 2,
    "best_posting_times": ["9:00 AM", "12:00 PM", "5:00 PM"]
  }
}
```

---

## 📈 Performance Metrics

### Evaluation Criteria

1. **Debate Quality**
   - Agents show genuine conflict
   - Arguments are specific and strategic
   - Decisions are well-reasoned

2. **Learning Evidence**
   - Agent weights change over iterations
   - Strategy shifts based on performance
   - Improved outcomes after learning

3. **Content Quality**
   - Platform-optimized formatting
   - Professional copywriting
   - Relevant hashtags and timing

4. **System Autonomy**
   - No human intervention needed
   - Self-correcting based on feedback
   - Adapts to new inputs dynamically

---

## 🚧 Troubleshooting

### Common Issues

**Problem:** `GROQ_API_KEY not found`
```bash
# Solution: Check .env file
cp .env.example .env
# Edit .env and add your API key
```

**Problem:** Image generation fails
```bash
# Solution 1: Check HuggingFace token
# Solution 2: Disable image generation
generate_image=False
```

**Problem:** Trends API rate limited
```bash
# Solution: Use sample trends
use_api_trends=False
```

### Debug Mode

```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 🎯 Hackathon Demo Strategy

### 5-Minute Presentation Flow

1. **Problem** (30s)
   - "Marketing teams spend hours debating strategy"
   - "We built an AI council that debates for you"

2. **Demo Setup** (30s)
   - Show brand input form
   - Enter product details
   - Click "Run Campaign"

3. **Live Debate** (2min)
   - Show agent proposals in real-time
   - Highlight conflicting perspectives
   - Display arbitrator's decision

4. **Generated Content** (1min)
   - Show platform-optimized post
   - Display AI-generated image
   - Review engagement prediction

5. **Learning Proof** (1min)
   - Run second iteration with same input
   - Show weight changes
   - Demonstrate strategy shift
   - "The system learned!"

### Key Talking Points

✅ "Unlike scheduling tools, our agents **debate** strategy"
✅ "Watch them disagree - Viral wants risk, Brand wants safety"
✅ "The Arbitrator weighs arguments using past performance"
✅ "It **learns** - weights shift based on what works"
✅ "Fully autonomous - no human clicks after 'Run Campaign'"

---

## 🛠️ Future Enhancements

### Phase 1 (Current)
- ✅ 5-agent debate system
- ✅ Text + image generation
- ✅ Learning via weight adjustment
- ✅ Streamlit dashboard

### Phase 2 (Planned)
- [ ] Real social media posting (Twitter API)
- [ ] A/B testing framework
- [ ] Sentiment analysis on real comments
- [ ] Multi-day campaign orchestration

### Phase 3 (Vision)
- [ ] Video content generation
- [ ] Cross-platform analytics
- [ ] Competitor analysis integration
- [ ] Voice-based agent personalities

---

## 📚 Technical Stack

| Component | Technology | Why Chosen |
|-----------|-----------|------------|
| LLM | Groq (Llama 3.1 70B) | Free, fast, high-quality |
| Image Gen | HuggingFace SDXL | Free, stable diffusion |
| Trends | Google + Reddit APIs | Real-time, diverse sources |
| UI | Streamlit | Rapid prototyping, interactive |
| Memory | JSON files | Simple, portable, debuggable |

---

## 🤝 Contributing

This is a hackathon project, but contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Anthropic** - Claude API for agent intelligence
- **Meta** - Llama models via Groq
- **Stability AI** - Stable Diffusion for images
- **Streamlit** - Rapid UI development
- **HackFusion** - Hackathon inspiration

---

## 📞 Contact

**Team:** 
Mudit Jain : 

**Project Link:** [https://github.com/Captain-MUDIT/mutli-agent-ai-counsil-for-social-media](https://github.com/Captain-MUDIT/mutli-agent-ai-counsil-for-social-media)



---

<div align="center">

**Built with ❤️ for HackFusion 2024**

⭐ Star this repo if you found it helpful!

</div>