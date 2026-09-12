from amazon_ai_coo.connectors.sellersprite import (
    get_sellersprite_tool,
    list_sellersprite_tools,
    load_sellersprite_registry,
    should_prefer_amazon_first,
)


def test_registry_contains_verified_45_tools() -> None:
    registry = load_sellersprite_registry()
    tools = registry["tools"]

    assert registry["verified_at"] == "2026-09-12"
    assert len(tools) == 45
    assert len({tool["code"] for tool in tools}) == 45


def test_key_tool_categories_are_queryable() -> None:
    assert get_sellersprite_tool("asin_competitor")["category"] == "product_asin"
    assert get_sellersprite_tool("keyword_conversion")["category"] == "keyword_aba"
    assert get_sellersprite_tool("market_research")["category"] == "market"
    assert get_sellersprite_tool("review")["category"] == "review"
    assert get_sellersprite_tool("trademark_list")["category"] == "trademark"
    assert len(list_sellersprite_tools("traffic")) == 4


def test_amazon_is_preferred_for_equivalent_seller_owned_facts() -> None:
    assert should_prefer_amazon_first(
        seller_owned_fact=True,
        amazon_equivalent_available=True,
    )
    assert not should_prefer_amazon_first(
        seller_owned_fact=False,
        amazon_equivalent_available=True,
    )
    assert not should_prefer_amazon_first(
        seller_owned_fact=True,
        amazon_equivalent_available=False,
    )
