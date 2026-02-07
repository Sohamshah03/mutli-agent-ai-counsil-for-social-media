"""
Debate Orchestration Module
Manages the agent debate process and decision-making
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple
from src.agents import MarketingAgent, Arbitrator, load_agents
from src.trends import TrendFetcher
from src.content_gen import ContentGenerator


class DebateOrchestrator:
    """Orchestrates the multi-agent debate process"""
    
    def __init__(self, agents: Dict[str, MarketingAgent] = None):
        if agents is None:
            self.agents = load_agents()
        else:
            self.agents = agents
        
        self.trend_fetcher = TrendFetcher()
        self.content_generator = ContentGenerator()
        self.debate_history = []
    
    def run_campaign_iteration(self, context: Dict, use_api_trends: bool = True, 
                               generate_image: bool = True) -> Dict:
        """Run one complete campaign iteration"""
        
        iteration_data = {
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "trends": [],
            "proposals": {},
            "critiques": {},
            "decision": {},
            "content": {},
            "engagement": {},
            "weight_updates": {}
        }
        
        print("\n" + "="*80)
        print("🎯 STARTING CAMPAIGN ITERATION")
        print("="*80)
        
        # Step 1: Fetch trends
        print("\n📊 Step 1: Fetching trending topics...")
        trends = self.trend_fetcher.fetch_all_trends(use_apis=use_api_trends, limit=10)
        trends_formatted = self.trend_fetcher.format_trends_for_context(trends)
        context['trends'] = trends_formatted
        iteration_data['trends'] = trends
        
        print(f"✅ Found {len(trends)} trends")
        for i, trend in enumerate(trends[:5], 1):
            print(f"   {i}. {trend['topic']}")
        
        # Step 2: Agent proposals (parallel)
        print("\n💡 Step 2: Agents proposing ideas...")
        proposals = {}
        
        for agent_id, agent in self.agents.items():
            if agent_id == "arbitrator":
                continue
            
            print(f"   🤖 {agent.name} proposing...")
            proposal = agent.propose(context)
            proposals[agent_id] = proposal
            iteration_data['proposals'][agent_id] = proposal
        
        print(f"✅ Received {len(proposals)} proposals")
        
        # Step 3: Agent critiques
        print("\n🗣️  Step 3: Agents debating proposals...")
        critiques = {}
        
        for agent_id, agent in self.agents.items():
            if agent_id == "arbitrator":
                continue
            
            print(f"   🤖 {agent.name} critiquing...")
            critique = agent.critique(context, proposals)
            critiques[agent_id] = critique
            iteration_data['critiques'][agent_id] = critique
        
        print(f"✅ Received {len(critiques)} critiques")
        
        # Step 4: Arbitrator decision
        print("\n⚖️  Step 4: Arbitrator making final decision...")
        arbitrator = self.agents['arbitrator']
        
        # Get current weights
        agent_weights = {
            agent_id: agent.voting_weight 
            for agent_id, agent in self.agents.items() 
            if agent_id != "arbitrator"
        }
        
        decision = arbitrator.decide(context, proposals, critiques, agent_weights)
        iteration_data['decision'] = decision
        
        print(f"✅ Decision made!")
        print(f"   Winner: {decision.get('winner', 'unknown')}")
        print(f"   Confidence: {decision.get('confidence', 'N/A')}/10")
        
        # Step 5: Content generation
        print("\n📝 Step 5: Generating content...")
        
        # Determine platform from decision
        platform = self._extract_platform(decision.get('implementation', ''))
        
        content = self.content_generator.generate_complete_post(
            decision, 
            context, 
            platform=platform,
            generate_image=generate_image
        )
        iteration_data['content'] = content
        
        print(f"✅ Content generated for {platform}")
        print(f"   Caption preview: {content['caption'][:80]}...")
        
        # Step 6: Simulate engagement
        print("\n📈 Step 6: Simulating engagement...")
        engagement = self._simulate_engagement(decision, content)
        iteration_data['engagement'] = engagement
        
        print(f"✅ Engagement simulated")
        print(f"   Likes: {engagement['likes']}")
        print(f"   Shares: {engagement['shares']}")
        print(f"   Sentiment: {engagement['sentiment']:.0%} positive")
        print(f"   Overall Score: {engagement['overall_score']:.1f}/10")
        
        # Step 7: Update agent weights (learning)
        print("\n🧠 Step 7: Updating agent weights (learning)...")
        weight_updates = self._update_agent_weights(decision, engagement)
        iteration_data['weight_updates'] = weight_updates
        
        for agent_id, update in weight_updates.items():
            print(f"   {agent_id}: {update['old_weight']:.2f} → {update['new_weight']:.2f}")
        
        # Save iteration data
        self.debate_history.append(iteration_data)
        self._save_iteration(iteration_data)
        
        print("\n" + "="*80)
        print("✅ ITERATION COMPLETE")
        print("="*80)
        
        return iteration_data
    
    def _extract_platform(self, implementation_text: str) -> str:
        """Extract platform from implementation text"""
        
        text_lower = implementation_text.lower()
        
        if 'twitter' in text_lower or 'x.com' in text_lower:
            return 'twitter'
        elif 'instagram' in text_lower or 'ig' in text_lower:
            return 'instagram'
        elif 'linkedin' in text_lower:
            return 'linkedin'
        else:
            return 'twitter'  # Default
    
    def _simulate_engagement(self, decision: Dict, content: Dict) -> Dict:
        """Simulate post engagement with random data"""
        
        import random
        
        # Base ranges
        base_likes = random.randint(2000, 8000)
        base_shares = random.randint(100, 500)
        base_comments = random.randint(50, 200)
        
        # Sentiment (random but biased positive)
        sentiment = random.uniform(0.6, 0.9)
        
        # Calculate overall score (0-10)
        overall_score = (
            (base_likes / 1000) * 0.4 +
            (base_shares / 100) * 0.3 +
            (base_comments / 50) * 0.2 +
            (sentiment * 10) * 0.1
        )
        overall_score = min(10, overall_score)
        
        return {
            "likes": base_likes,
            "shares": base_shares,
            "comments": base_comments,
            "sentiment": sentiment,
            "overall_score": overall_score,
            "platform": content.get('platform', 'twitter')
        }
    
    def _update_agent_weights(self, decision: Dict, engagement: Dict) -> Dict:
        """Update agent voting weights based on performance"""
        
        winner_id = decision.get('winner', 'unknown')
        performance_score = engagement.get('overall_score', 5.0)
        
        weight_updates = {}
        
        for agent_id, agent in self.agents.items():
            if agent_id == "arbitrator":
                continue
            
            old_weight = agent.voting_weight
            
            # Winner gets boosted by performance
            if agent_id == winner_id:
                agent.update_weight(performance_score, learning_rate=0.2)
            else:
                # Losers get slight penalty
                agent.update_weight(performance_score * 0.5, learning_rate=0.1)
            
            weight_updates[agent_id] = {
                "old_weight": old_weight,
                "new_weight": agent.voting_weight,
                "change": agent.voting_weight - old_weight,
                "was_winner": agent_id == winner_id
            }
        
        return weight_updates
    
    def _save_iteration(self, iteration_data: Dict):
        """Save iteration data to file"""
        
        os.makedirs("outputs/debate_logs", exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"outputs/debate_logs/iteration_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(iteration_data, f, indent=2)
        
        print(f"\n💾 Iteration saved: {filename}")
    
    def get_weight_history(self) -> Dict[str, List[float]]:
        """Get weight evolution over iterations"""
        
        history = {}
        
        for agent_id in self.agents.keys():
            if agent_id == "arbitrator":
                continue
            
            history[agent_id] = []
            
            for iteration in self.debate_history:
                if 'weight_updates' in iteration and agent_id in iteration['weight_updates']:
                    history[agent_id].append(
                        iteration['weight_updates'][agent_id]['new_weight']
                    )
        
        return history
    
    def compare_iterations(self, iteration1: int, iteration2: int) -> Dict:
        """Compare two iterations"""
        
        if iteration1 >= len(self.debate_history) or iteration2 >= len(self.debate_history):
            return {"error": "Invalid iteration numbers"}
        
        iter1 = self.debate_history[iteration1]
        iter2 = self.debate_history[iteration2]
        
        return {
            "iteration_1": {
                "winner": iter1['decision'].get('winner'),
                "engagement": iter1['engagement'].get('overall_score'),
                "weights": {
                    agent_id: update['new_weight']
                    for agent_id, update in iter1.get('weight_updates', {}).items()
                }
            },
            "iteration_2": {
                "winner": iter2['decision'].get('winner'),
                "engagement": iter2['engagement'].get('overall_score'),
                "weights": {
                    agent_id: update['new_weight']
                    for agent_id, update in iter2.get('weight_updates', {}).items()
                }
            },
            "changes": {
                "winner_changed": iter1['decision'].get('winner') != iter2['decision'].get('winner'),
                "engagement_diff": iter2['engagement'].get('overall_score', 0) - iter1['engagement'].get('overall_score', 0)
            }
        }


if __name__ == "__main__":
    print("Testing Debate Orchestrator...\n")
    
    # Test context
    context = {
        "brand_name": "TechFlow AI",
        "industry": "Technology / SaaS",
        "product_info": "Smart Scheduling Assistant - AI-powered calendar optimization that saves 5 hours per week",
        "target_audience": "Busy professionals, startup founders, tech enthusiasts aged 25-45"
    }
    
    orchestrator = DebateOrchestrator()
    
    # Run one iteration (no image for quick test)
    result = orchestrator.run_campaign_iteration(
        context, 
        use_api_trends=False,  # Use sample trends for testing
        generate_image=False   # Skip image for speed
    )
    
    print("\n✅ Test complete!")