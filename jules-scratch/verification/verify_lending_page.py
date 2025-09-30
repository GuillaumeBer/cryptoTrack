from playwright.sync_api import Page, expect
import re

def test_jupiter_lending_monitor(page: Page):
    """
    This test verifies the functionality of the Jupiter Lend monitoring page.
    1. Navigates to the application.
    2. Clicks the "Jupiter Lending" navigation button.
    3. Enters a wallet address ('DEMO') into the input field.
    4. Clicks the "Rechercher les Positions" button.
    5. Verifies that the position cards are displayed with the correct data.
    6. Takes a screenshot of the final state.
    """
    # 1. Arrange: Go to the application's homepage.
    # Since the dev server isn't working, we assume the app is served at the root.
    # In a real scenario, this would be http://localhost:3000
    page.goto("http://localhost:8000")

    # 2. Act: Navigate to the Jupiter Lending page.
    lending_button = page.get_by_role("button", name="Jupiter Lending")
    expect(lending_button).to_be_visible()
    lending_button.click()

    # 3. Act: Enter the demo wallet address and fetch positions.
    wallet_input = page.get_by_placeholder("Entrez l'adresse du portefeuille Solana ou 'DEMO'")
    expect(wallet_input).to_be_visible()
    wallet_input.fill("DEMO")

    fetch_button = page.get_by_role("button", name="Rechercher les Positions")
    expect(fetch_button).to_be_enabled()
    fetch_button.click()

    # 4. Assert: Verify the position cards are displayed correctly.
    # We expect to see two cards based on the backend's demo data.

    # Verify the first card (SOL/USDC)
    sol_card = page.locator(".position-card", has_text="SOL").first
    expect(sol_card).to_be_visible()
    expect(sol_card.get_by_text("Collatéral")).to_be_visible()
    expect(sol_card.get_by_text("$1500.50")).to_be_visible()
    expect(sol_card.get_by_text("LTV")).to_be_visible()
    expect(sol_card.get_by_text("50.00%")).to_be_visible()
    expect(sol_card.get_by_text(re.compile(r"RISQUE :.SAFE"))).to_be_visible()

    # Verify the second card (JitoSOL/USDT)
    jitosol_card = page.locator(".position-card", has_text="JitoSOL").first
    expect(jitosol_card).to_be_visible()
    expect(jitosol_card.get_by_text("Collatéral")).to_be_visible()
    expect(jitosol_card.get_by_text("$2500.00")).to_be_visible()
    expect(jitosol_card.get_by_text("LTV")).to_be_visible()
    expect(jitosol_card.get_by_text("72.00%")).to_be_visible()
    expect(jitosol_card.get_by_text(re.compile(r"RISQUE :.RISKY"))).to_be_visible()

    # 5. Screenshot: Capture the final result for visual verification.
    page.screenshot(path="jules-scratch/verification/lending_page.png")