"""
Test Suite for AI Marketing Council
Run this to verify all components work before demo
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()


def test_environment():
    """Test environment variables and API keys"""
    print("\n" + "="*60)
    print("TEST 1: Environment Variables")
    print("="*60)
    
    required_keys = ["GROQ_API_KEY", "HUGGINGFACE_TOKEN"]
    optional_keys = ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET"]
    
    all_good = True
    
    for key in required_keys:
        value = os.getenv(key)
        if value and value != f"your_{key.lower()}_here":
            print(f"✅ {key}: Configured")
        else:
            print(f"❌ {key}: Missing or not configured")
            all_good = False
    
    for key in optional_keys:
        value = os.getenv(key)
        if value and value != f"your_{key.lower()}":
            print(f"✅ {key}: Configured (optional)")
        else:
            print(f"⚠️  {key}: Not configured (optional, using fallback)")
    
    return all_good


def test_imports():
    """Test that all required packages are installed"""
    print("\n" + "="*60)
    print("TEST 2: Package Imports")
    print("="*60)
    
    packages = {
        "groq": "Groq",
        "streamlit": "Streamlit",
        "plotly": "Plotly",
        "pandas": "Pandas",
        "dotenv": "python-dotenv",
        "huggingface_hub": "HuggingFace Hub",
        "PIL": "Pillow"
    }
    
    all_good = True
    
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - Run: pip install -r requirements.txt")
            all_good = False
    
    # Optional packages
    try:
        import praw
        print(f"✅ praw (optional)")
    except ImportError:
        print(f"⚠️  praw (optional, for Reddit trends)")
    
    try:
        import pytrends
        print(f"✅ pytrends (optional)")
    except ImportError:
        print(f"⚠️  pytrends (optional, for Google Trends)")
    
    return all_good


def test_agents():
    """Test agent system"""
    print("\n" + "="*60)
    print("TEST 3: Agent System")
    print("="*60)
    
    try:
        from src.agents import load_agents
        
        agents = load_agents()
        print(f"✅ Loaded {len(agents)} agents")
        
        for agent_id, agent in agents.items():
            print(f"   - {agent.name} ({agent_id})")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent loading failed: {str(e)}")
        return False


def test_trends():
    """Test trend fetching"""
    print("\n" + "="*60)
    print("TEST 4: Trend Fetching")
    print("="*60)
    
    try:
        from src.trends import TrendFetcher
        
        fetcher = TrendFetcher()
        
        # Test sample trends (should always work)
        trends = fetcher.get_sample_trends(limit=5)
        print(f"✅ Sample trends: {len(trends)} topics")
        for trend in trends[:3]:
            print(f"   - {trend['topic']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Trend fetching failed: {str(e)}")
        return False


def test_groq_api():
    """Test Groq API connection"""
    print("\n" + "="*60)
    print("TEST 5: Groq API Connection")
    print("="*60)
    
    try:
        from groq import Groq
        
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": "Say 'API works!' in exactly 3 words."}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ Groq API connected")
        print(f"   Response: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Groq API failed: {str(e)}")
        print(f"   Check your GROQ_API_KEY in .env file")
        return False


def test_content_generation():
    """Test content generation (without image)"""
    print("\n" + "="*60)
    print("TEST 6: Content Generation")
    print("="*60)
    
    try:
        from src.content_gen import ContentGenerator
        
        generator = ContentGenerator()
        
        # Mock decision and context
        decision = {
            "decision": "Create engaging post",
            "implementation": "Platform: Twitter",
            "winner": "viral_hunter"
        }
        
        context = {
            "brand_name": "Test Brand",
            "product_info": "Test Product",
            "target_audience": "Tech users"
        }
        
        # Generate text only (fast)
        post = generator.generate_post_text(decision, context, "twitter")
        
        print(f"✅ Text generation works")
        print(f"   Platform: {post['platform']}")
        print(f"   Caption: {post['caption'][:60]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Content generation failed: {str(e)}")
        return False


def test_full_iteration():
    """Test complete iteration (no image for speed)"""
    print("\n" + "="*60)
    print("TEST 7: Full Campaign Iteration")
    print("="*60)
    
    try:
        from src.debate import DebateOrchestrator
        
        orchestrator = DebateOrchestrator()
        
        context = {
            "brand_name": "Test Brand",
            "industry": "Technology",
            "product_info": "AI Product Test",
            "target_audience": "Tech professionals"
        }
        
        print("⏳ Running test iteration (this may take 30-60 seconds)...")
        
        result = orchestrator.run_campaign_iteration(
            context,
            use_api_trends=False,  # Use samples for speed
            generate_image=False   # Skip image for speed
        )
        
        print(f"\n✅ Full iteration completed!")
        print(f"   Winner: {result['decision'].get('winner', 'unknown')}")
        print(f"   Engagement Score: {result['engagement'].get('overall_score', 0):.1f}/10")
        print(f"   Caption preview: {result['content']['caption'][:80]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Full iteration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_directories():
    """Test that output directories exist"""
    print("\n" + "="*60)
    print("TEST 8: Directory Structure")
    print("="*60)
    
    dirs = [
        "outputs",
        "outputs/generated_images",
        "outputs/debate_logs",
        "config",
        "data",
        "src"
    ]
    
    all_good = True
    
    for dir_path in dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ - Creating...")
            os.makedirs(dir_path, exist_ok=True)
    
    return all_good


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print(" "*20 + "AI MARKETING COUNCIL - TEST SUITE")
    print("="*70)
    
    results = {
        "Environment": test_environment(),
        "Imports": test_imports(),
        "Directories": test_directories(),
        "Agents": test_agents(),
        "Trends": test_trends(),
        "Groq API": test_groq_api(),
        "Content Gen": test_content_generation(),
        "Full Iteration": test_full_iteration()
    }
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "="*70)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("="*70)
    
    if passed == total:
        print("\n🎉 All tests passed! System ready for demo.")
        print("\nNext steps:")
        print("1. Run: streamlit run app.py")
        print("2. Test in browser")
        print("3. Run 2-3 campaigns to prepare for demo")
    else:
        print("\n⚠️  Some tests failed. Fix issues before demo:")
        print("\nCommon fixes:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Configure API keys in .env file")
        print("- Check internet connection")
    
    print()


if __name__ == "__main__":
    run_all_tests()