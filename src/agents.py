"""
AI Marketing Council - Agent System
Core agent implementation with Groq LLM integration
"""

import os
import json
from groq import Groq
from dotenv import load_dotenv
from typing import Dict, List, Optional

load_dotenv()


class MarketingAgent:
    """Individual AI agent with specific role and personality"""
    
    def __init__(self, agent_id: str, config: Dict):
        self.agent_id = agent_id
        self.name = config["name"]
        self.role = config["role"]
        self.personality = config["personality"]
        self.goals = config["goals"]
        self.voting_weight = config.get("voting_weight", 1.0)
        self.color = config.get("color", "#000000")
        
        # Initialize Groq client
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
        
        # Performance history
        self.history = []
    
    def _create_system_prompt(self) -> str:
        """Create system prompt for this agent"""
        return f"""You are {self.name}, a member of an AI Marketing Council.

ROLE: {self.role}

PERSONALITY: {self.personality}

YOUR GOALS:
{chr(10).join(f"- {goal}" for goal in self.goals)}

INSTRUCTIONS:
- Advocate strongly for your perspective
- Provide specific, actionable recommendations
- Critique other agents' proposals when they conflict with your goals
- Be concise but thorough in your reasoning
- Always explain WHY you support or oppose an idea
- Stay in character at all times
"""
    
    def propose(self, context: Dict) -> str:
        """Generate a proposal based on context"""
        
        user_prompt = f"""BRAND CONTEXT:
Brand: {context.get('brand_name', 'Unknown')}
Industry: {context.get('industry', 'Tech')}
Target Audience: {context.get('target_audience', 'General')}

PRODUCT/CAMPAIGN:
{context.get('product_info', 'No product info provided')}

TRENDING TOPICS:
{chr(10).join(f"- {trend}" for trend in context.get('trends', [])[:5])}

TASK: Propose 2-3 specific social media post ideas for this campaign. For each idea:
1. Specify the platform (Twitter, Instagram, or LinkedIn)
2. Describe the content approach
3. Explain why it aligns with your goals
4. Rate its potential (1-10) from your perspective

Be specific and strategic."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._create_system_prompt()},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating proposal: {str(e)}"
    
    def critique(self, context: Dict, proposals: Dict[str, str]) -> str:
        """Critique other agents' proposals"""
        
        proposals_text = "\n\n".join([
            f"--- {agent_name.upper()} PROPOSAL ---\n{proposal}"
            for agent_name, proposal in proposals.items()
            if agent_name != self.agent_id
        ])
        
        user_prompt = f"""BRAND CONTEXT:
Brand: {context.get('brand_name', 'Unknown')}
Product: {context.get('product_info', 'N/A')}

OTHER AGENTS' PROPOSALS:
{proposals_text}

TASK: Critique these proposals from YOUR perspective ({self.name}).

For each proposal:
1. Identify what conflicts with your goals
2. Point out risks or missed opportunities
3. Suggest improvements if applicable
4. Rate each proposal (1-10) from your perspective

Be direct and specific. This is a debate, not a collaboration."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._create_system_prompt()},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating critique: {str(e)}"
    
    def update_weight(self, performance_score: float, learning_rate: float = 0.2):
        """Update voting weight based on performance"""
        
        # Performance score: 0-10 scale
        # If score > 7: increase weight
        # If score < 5: decrease weight
        
        if performance_score >= 7:
            adjustment = learning_rate * (performance_score - 7) / 3
            self.voting_weight += adjustment
        elif performance_score < 5:
            adjustment = learning_rate * (5 - performance_score) / 5
            self.voting_weight -= adjustment
        
        # Keep weight in reasonable bounds
        self.voting_weight = max(0.5, min(2.0, self.voting_weight))
        
        # Record history
        self.history.append({
            "performance_score": performance_score,
            "new_weight": self.voting_weight
        })
    
    def get_stats(self) -> Dict:
        """Get agent statistics"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "current_weight": self.voting_weight,
            "color": self.color,
            "history_length": len(self.history)
        }


class Arbitrator(MarketingAgent):
    """Special agent that makes final decisions"""
    
    def decide(self, context: Dict, proposals: Dict[str, str], 
               critiques: Dict[str, str], agent_weights: Dict[str, float]) -> Dict:
        """Make final decision based on all inputs"""
        
        # Compile all debate content
        debate_summary = "PROPOSALS:\n"
        for agent_id, proposal in proposals.items():
            debate_summary += f"\n{agent_id.upper()} (weight: {agent_weights.get(agent_id, 1.0):.2f}):\n{proposal}\n"
        
        debate_summary += "\n\nCRITIQUES:\n"
        for agent_id, critique in critiques.items():
            debate_summary += f"\n{agent_id.upper()}:\n{critique}\n"
        
        user_prompt = f"""BRAND CONTEXT:
Brand: {context.get('brand_name', 'Unknown')}
Product: {context.get('product_info', 'N/A')}

FULL DEBATE:
{debate_summary}

AGENT VOTING WEIGHTS (based on past performance):
{chr(10).join(f"- {agent_id}: {weight:.2f}" for agent_id, weight in agent_weights.items())}

TASK: As the Arbitrator, make the final decision.

Provide your response in this EXACT format:

DECISION: [Choose the best approach - can be one agent's proposal or a hybrid]

WINNER: [Agent ID of primary winner - e.g., viral_hunter, brand_guardian, etc.]

CONFIDENCE: [Your confidence in this decision, 1-10]

REASONING: [Detailed explanation of why this is the best choice, considering:
- Strategic alignment with brand goals
- Risk vs reward trade-off
- Agent voting weights
- Platform optimization
- Expected performance]

IMPLEMENTATION: [Specific details of the final post strategy:
- Platform: [Twitter/Instagram/LinkedIn]
- Content approach: [Brief description]
- Key message: [Main point to communicate]
- Tone: [Professional/Casual/Bold/etc.]
]
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._create_system_prompt()},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6,
                max_tokens=1000
            )
            
            decision_text = response.choices[0].message.content
            
            # Parse decision
            result = {
                "full_response": decision_text,
                "decision": self._extract_field(decision_text, "DECISION"),
                "winner": self._extract_field(decision_text, "WINNER"),
                "confidence": self._extract_field(decision_text, "CONFIDENCE"),
                "reasoning": self._extract_field(decision_text, "REASONING"),
                "implementation": self._extract_field(decision_text, "IMPLEMENTATION")
            }
            
            return result
            
        except Exception as e:
            return {
                "full_response": f"Error: {str(e)}",
                "decision": "Unable to decide",
                "winner": "none",
                "confidence": "0",
                "reasoning": str(e),
                "implementation": "N/A"
            }
    
    def _extract_field(self, text: str, field_name: str) -> str:
        """Extract a field from the decision text"""
        try:
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith(field_name + ":"):
                    # Get content after the field name
                    content = line.split(":", 1)[1].strip()
                    
                    # For multi-line fields, collect until next field or end
                    if field_name in ["REASONING", "IMPLEMENTATION"]:
                        j = i + 1
                        while j < len(lines) and not any(
                            lines[j].strip().startswith(f + ":") 
                            for f in ["DECISION", "WINNER", "CONFIDENCE", "REASONING", "IMPLEMENTATION"]
                        ):
                            content += "\n" + lines[j]
                            j += 1
                    
                    return content.strip()
            
            return "Not specified"
        except Exception:
            return "Parse error"


def load_agents(config_path: str = "config/agents.json") -> Dict[str, MarketingAgent]:
    """Load all agents from configuration"""
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    agents = {}
    
    for agent_id, agent_config in config["agents"].items():
        if agent_id == "arbitrator":
            agents[agent_id] = Arbitrator(agent_id, agent_config)
        else:
            agents[agent_id] = MarketingAgent(agent_id, agent_config)
    
    return agents


if __name__ == "__main__":
    # Test agent creation
    print("Testing agent system...")
    
    agents = load_agents()
    
    print(f"\nLoaded {len(agents)} agents:")
    for agent_id, agent in agents.items():
        stats = agent.get_stats()
        print(f"  - {stats['name']} ({agent_id})")
    
    print("\n✅ Agent system initialized successfully!")