from browser_use import Tools,Agent, ChatOpenAI, ActionResult, Browser

from dotenv import load_dotenv
import asyncio
tools = Tools()

load_dotenv()



async def main():
    llm = ChatOpenAI(model="gpt-4.1-mini")
    # llm = ChatOllama(model="llama3.2:1b")
    task = """
    1. Go to https://indeed.com
    2. find 5 relevant job postings for "Laravel developer" in "Egypt"
    3. For each job posting, use extract action to get the job title, company name, location
    4. Summarize the job description in one sentence
    5. use screenshot action to screenshot the job posting page
    6. use write_file action to store the extracted information in a CSV file named "job_postings.csv" with columns: Job Title, Company Name, Location, Summary, Screenshot Path

    note: Use as few steps as possible, any executed code must be in javascript 
    """
    agent = Agent(
        task=task,
        llm=llm,
    )
    await agent.run()




if __name__ == "__main__":
    asyncio.run(main())