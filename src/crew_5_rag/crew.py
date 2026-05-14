from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, SeleniumScrapingTool, ScrapeWebsiteTool
from .tools.custom_tool import StoreReportTool, RAGRetrievalTool, make_store_callback

search_tool          = SerperDevTool()
store_tool           = StoreReportTool()
rag_tool             = RAGRetrievalTool()
web_scrape_tool      = ScrapeWebsiteTool()
web_scrape_selenium  = SeleniumScrapingTool()

tool_kit = [search_tool, store_tool, rag_tool, web_scrape_tool, web_scrape_selenium]

@CrewBase
class MarketResearchCrew:

    agents_config = "config/agents.yaml"
    tasks_config  = "config/tasks.yaml"

    # ── Agents ────────────────────────────────────────────────────────────────

    @agent
    def market_research_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["market_research_analyst"],
            tools=tool_kit,
            verbose=True,
        )

    @agent
    def competitor_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["competitor_researcher"],
            tools=tool_kit,
            verbose=True,
        )

    @agent
    def customer_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["customer_researcher"],
            tools=tool_kit,
            verbose=True,
        )

    @agent
    def product_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["product_researcher"],
            tools=tool_kit,
            verbose=True,
        )

    @agent
    def business_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["business_analyst"],
            tools=[rag_tool],
            verbose=True,
        )

    # ── Tasks — callback here, NOT on agent ───────────────────────────────────

    @task
    def market_research_task(self) -> Task:
        return Task(
            config=self.tasks_config["market_research_task"],
            callback=make_store_callback("market_research_analyst")
        )

    @task
    def competitor_research_task(self) -> Task:
        return Task(
            config=self.tasks_config["competitor_research_task"],
            callback=make_store_callback("competitor_researcher")
        )

    @task
    def customer_research_task(self) -> Task:
        return Task(
            config=self.tasks_config["customer_research_task"],
            callback=make_store_callback("customer_researcher")
        )

    @task
    def product_research_task(self) -> Task:
        return Task(
            config=self.tasks_config["product_research_task"],
            callback=make_store_callback("product_researcher")
        )

    @task
    def business_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["business_analysis_task"],
            output_file="final_report_2.md",
        )

    # ── Crew ──────────────────────────────────────────────────────────────────

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )