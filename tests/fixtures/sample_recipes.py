"""Sample recipe data for testing.

This module provides comprehensive sample recipe data that can be used
across all test modules. Includes recipes from different categories,
various complexity levels, and edge cases for thorough testing.
"""

from recipe_fmt.models.recipe import Ingredient, Nutrition, Recipe

# Sample Breakfast Recipe - Perfect Pancakes
SAMPLE_PANCAKES = Recipe(
    title="Perfect Pancakes",
    category="Breakfast",
    description="Fluffy buttermilk pancakes that are perfect for weekend mornings",
    prep_time_minutes=10,
    cook_time_minutes=15,
    servings=4,
    difficulty="Easy",
    ingredients=[
        Ingredient(
            ingredient="all-purpose flour",
            amount=2.0,
            unit="cups",
            weight_grams=240,
            purpose="base",
        ),
        Ingredient(
            ingredient="granulated sugar",
            amount=2.0,
            unit="TBL",
            weight_grams=25,
            purpose="sweetening",
        ),
        Ingredient(ingredient="baking powder", amount=2.0, unit="tsp", weight_grams=8, purpose="leavening"),
        Ingredient(ingredient="salt", amount=1.0, unit="tsp", weight_grams=5, purpose="flavor enhancement"),
        Ingredient(ingredient="buttermilk", amount=1.5, unit="cups", weight_grams=360, purpose="liquid"),
        Ingredient(ingredient="large eggs", amount=2.0, unit="whole", weight_grams=100, purpose="binding"),
        Ingredient(ingredient="unsalted butter", amount=4.0, unit="TBL", weight_grams=56, purpose="fat"),
    ],
    instructions=[
        "In a large bowl, whisk together flour, sugar, baking powder, and salt.",
        "In a separate bowl, whisk buttermilk, eggs, and melted butter until combined.",
        "Pour wet ingredients into dry ingredients and stir until just combined. Don't overmix - lumps are okay.",
        "Heat a griddle or large skillet over medium heat. Lightly grease with butter or oil.",
        "Pour 1/4 cup batter for each pancake. Cook until bubbles form on surface and edges look set, 2-3 minutes.",
        "Flip and cook until golden brown on other side, 1-2 minutes more.",
        "Serve immediately with butter and maple syrup.",
    ],
    notes=["Don't overmix the batter - lumpy is good!", "Keep cooked pancakes warm in 200°F oven"],
    tags=["breakfast", "pancakes", "weekend", "family-friendly"],
    nutrition=Nutrition(
        calories_per_serving=285,
        protein_grams=8.5,
        carbs_grams=42.0,
        fat_grams=9.2,
        fiber_grams=1.8,
        sugar_grams=8.5,
    ),
    source="Family Recipe Collection",
)

# Sample Meat Recipe - Beef Stew
SAMPLE_BEEF_STEW = Recipe(
    title="Classic Beef Stew",
    category="Meat",
    description="Hearty beef stew with tender vegetables in rich gravy",
    prep_time_minutes=20,
    cook_time_minutes=120,
    servings=6,
    difficulty="Medium",
    ingredients=[
        Ingredient(
            ingredient="beef chuck roast",
            amount=2.0,
            unit="pounds",
            weight_grams=907,
            purpose="protein",
        ),
        Ingredient(
            ingredient="all-purpose flour",
            amount=0.25,
            unit="cup",
            weight_grams=30,
            purpose="thickening",
        ),
        Ingredient(
            ingredient="vegetable oil",
            amount=2.0,
            unit="TBL",
            weight_grams=28,
            purpose="cooking fat",
        ),
        Ingredient(
            ingredient="yellow onion",
            amount=1.0,
            unit="large",
            weight_grams=200,
            purpose="aromatics",
        ),
        Ingredient(ingredient="carrots", amount=4.0, unit="large", weight_grams=240, purpose="vegetables"),
        Ingredient(
            ingredient="celery stalks",
            amount=3.0,
            unit="stalks",
            weight_grams=120,
            purpose="vegetables",
        ),
        Ingredient(ingredient="beef broth", amount=4.0, unit="cups", weight_grams=960, purpose="liquid"),
        Ingredient(ingredient="red wine", amount=1.0, unit="cup", weight_grams=240, purpose="flavor"),
        Ingredient(ingredient="tomato paste", amount=2.0, unit="TBL", weight_grams=32, purpose="umami"),
        Ingredient(ingredient="fresh thyme", amount=2.0, unit="sprigs", weight_grams=2, purpose="herbs"),
        Ingredient(ingredient="bay leaves", amount=2.0, unit="leaves", weight_grams=1, purpose="aromatics"),
        Ingredient(
            ingredient="Yukon Gold potatoes",
            amount=1.5,
            unit="pounds",
            weight_grams=680,
            purpose="starch",
        ),
    ],
    instructions=[
        "Cut beef into 2-inch chunks and pat dry. Season with salt and pepper, then toss with flour.",
        "Heat oil in a heavy Dutch oven over medium-high heat. Brown beef on all sides, working in batches.",
        "Remove beef and set aside. Reduce heat to medium and add onions to the pot.",
        "Cook onions until softened, about 5 minutes. Add tomato paste and cook 1 minute more.",
        "Add wine, scraping up any browned bits. Return beef to pot with broth, thyme, and bay leaves.",
        "Bring to a boil, then reduce heat to low, cover, and simmer 1 hour.",
        "Add carrots, celery, and potatoes. Continue simmering covered until beef is tender, about 1 hour more.",
        "Remove bay leaves and thyme stems. Adjust seasoning with salt and pepper.",
        "Serve hot with crusty bread.",
    ],
    notes=["Can be made 1 day ahead and reheated", "Freezes well for up to 3 months"],
    tags=["dinner", "comfort-food", "winter", "make-ahead", "freezer-friendly"],
    nutrition=Nutrition(
        calories_per_serving=485,
        protein_grams=35.2,
        carbs_grams=28.5,
        fat_grams=22.8,
        fiber_grams=4.2,
        sugar_grams=8.1,
    ),
    source="Grandma's Kitchen",
)

# Sample Dessert Recipe - Chocolate Cake
SAMPLE_CHOCOLATE_CAKE = Recipe(
    title="Rich Chocolate Cake",
    category="Dessert",
    description="Decadent double chocolate layer cake with fudge frosting",
    prep_time_minutes=30,
    cook_time_minutes=35,
    servings=12,
    difficulty="Hard",
    ingredients=[
        Ingredient(
            ingredient="all-purpose flour",
            amount=1.75,
            unit="cups",
            weight_grams=210,
            purpose="structure",
        ),
        Ingredient(
            ingredient="granulated sugar",
            amount=2.0,
            unit="cups",
            weight_grams=400,
            purpose="sweetening",
        ),
        Ingredient(
            ingredient="unsweetened cocoa powder",
            amount=0.75,
            unit="cup",
            weight_grams=75,
            purpose="chocolate flavor",
        ),
        Ingredient(ingredient="baking soda", amount=2.0, unit="tsp", weight_grams=8, purpose="leavening"),
        Ingredient(ingredient="baking powder", amount=1.0, unit="tsp", weight_grams=4, purpose="leavening"),
        Ingredient(ingredient="salt", amount=1.0, unit="tsp", weight_grams=5, purpose="flavor enhancement"),
        Ingredient(ingredient="large eggs", amount=2.0, unit="whole", weight_grams=100, purpose="binding"),
        Ingredient(ingredient="buttermilk", amount=1.0, unit="cup", weight_grams=240, purpose="liquid"),
        Ingredient(
            ingredient="strong black coffee",
            amount=1.0,
            unit="cup",
            weight_grams=240,
            purpose="chocolate enhancement",
        ),
        Ingredient(ingredient="vegetable oil", amount=0.5, unit="cup", weight_grams=120, purpose="fat"),
        Ingredient(ingredient="vanilla extract", amount=2.0, unit="tsp", weight_grams=8, purpose="flavor"),
    ],
    instructions=[
        "Preheat oven to 350°F. Grease two 9-inch round cake pans and dust with cocoa powder.",
        "In a large bowl, whisk together flour, sugar, cocoa powder, baking soda, baking powder, and salt.",
        "In another bowl, whisk together eggs, buttermilk, coffee, oil, and vanilla.",
        "Pour wet ingredients into dry ingredients and whisk until smooth.",
        "Divide batter evenly between prepared pans.",
        "Bake 30-35 minutes until a toothpick inserted in center comes out clean.",
        "Cool in pans 10 minutes, then turn out onto wire racks to cool completely.",
        "Frost with chocolate buttercream frosting when completely cool.",
    ],
    notes=["Coffee enhances chocolate flavor - don't omit!", "Can be made 2 days ahead"],
    tags=["dessert", "chocolate", "birthday", "special-occasion"],
    nutrition=Nutrition(
        calories_per_serving=425,
        protein_grams=6.8,
        carbs_grams=68.2,
        fat_grams=16.5,
        fiber_grams=4.1,
        sugar_grams=52.3,
    ),
    source="Chef's Collection",
)

# Sample Invalid Recipe for Error Testing
SAMPLE_INVALID_RECIPE = {
    "title": "",  # Invalid - empty title
    "category": "InvalidCategory",  # Invalid category
    "ingredients": [
        {
            "ingredient": "flour",
            "amount": -1.0,  # Invalid - negative amount
            "unit": "",  # Invalid - empty unit
            "weight_grams": "not_a_number",  # Invalid - wrong type
        }
    ],
    "instructions": [],  # Invalid - empty instructions
    "prep_time_minutes": "invalid",  # Invalid - wrong type
    "servings": 0,  # Invalid - zero servings
}

# Sample Recipe with Edge Cases
SAMPLE_EDGE_CASE_RECIPE = Recipe(
    title="A" * 100,  # Maximum length title
    category="Other",
    description="Recipe with edge case values for testing boundary conditions",
    prep_time_minutes=1,  # Minimum time
    cook_time_minutes=600,  # Long cook time (10 hours)
    servings=1,  # Minimum servings
    difficulty="Easy",
    ingredients=[
        Ingredient(
            ingredient="specialty ingredient with very long name that tests character limits",
            amount=0.125,  # Fractional amount
            unit="pinch",
            weight_grams=1,  # Minimum weight
            purpose="testing",
        ),
        Ingredient(
            ingredient="large quantity ingredient",
            amount=50.0,  # Large amount
            unit="pounds",
            weight_grams=22680,  # Large weight
            purpose="bulk",
        ),
    ],
    instructions=[
        "This is a very long instruction that tests the limits of instruction text "
        "length and ensures that our system can handle verbose cooking directions "
        "that might include detailed explanations, multiple techniques, and "
        "extensive background information about the cooking process.",
        "Short step.",
        "Another long instruction with unicode characters: ½ cup, 180°F, café, naïve, résumé, jalapeño",
    ],
    notes=["Edge case recipe for testing", "Contains unicode: ½ ¼ ¾ ° ™ ®"],
    tags=["testing", "edge-case", "unicode", "boundary-conditions"],
    source="Test Suite",
)

# Minimal Recipe for Testing Defaults
SAMPLE_MINIMAL_RECIPE = Recipe(
    title="Minimal Recipe",
    category="Other",
    ingredients=[Ingredient(ingredient="water", amount=1.0, unit="cup")],
    instructions=["Drink the water."],
)

# Collection of all sample recipes
ALL_SAMPLE_RECIPES = {
    "pancakes": SAMPLE_PANCAKES,
    "beef_stew": SAMPLE_BEEF_STEW,
    "chocolate_cake": SAMPLE_CHOCOLATE_CAKE,
    "invalid": SAMPLE_INVALID_RECIPE,
    "edge_case": SAMPLE_EDGE_CASE_RECIPE,
    "minimal": SAMPLE_MINIMAL_RECIPE,
}

# Sample markdown recipe content for file testing
SAMPLE_MARKDOWN_CONTENT = {
    "pancakes": """# Perfect Pancakes

*Fluffy buttermilk pancakes that are perfect for weekend mornings*

**Category:** Breakfast
**Prep Time:** 10 minutes
**Cook Time:** 15 minutes
**Servings:** 4
**Difficulty:** Easy

## Ingredients

- 2 cups all-purpose flour
- 2 TBL granulated sugar
- 2 tsp baking powder
- 1 tsp salt
- 1.5 cups buttermilk
- 2 large eggs
- 4 TBL unsalted butter, melted

## Instructions

1. In a large bowl, whisk together flour, sugar, baking powder, and salt.
2. In a separate bowl, whisk buttermilk, eggs, and melted butter until combined.
3. Pour wet ingredients into dry ingredients and stir until just combined. \
Don't overmix - lumps are okay.
4. Heat a griddle or large skillet over medium heat. Lightly grease with butter or oil.
5. Pour 1/4 cup batter for each pancake. Cook until bubbles form on surface \
and edges look set, about 2-3 minutes.
6. Flip and cook until golden brown on other side, 1-2 minutes more.
7. Serve immediately with butter and maple syrup.

## Notes

- Don't overmix the batter - lumpy is good!
- Keep cooked pancakes warm in 200°F oven

**Tags:** breakfast, pancakes, weekend, family-friendly
""",
    "beef_stew": """# Classic Beef Stew

*Hearty beef stew with tender vegetables in rich gravy*

**Category:** Meat
**Prep Time:** 20 minutes
**Cook Time:** 2 hours
**Servings:** 6
**Difficulty:** Medium

## Ingredients

- 2 pounds beef chuck roast, cut into 2-inch chunks
- 1/4 cup all-purpose flour
- 2 TBL vegetable oil
- 1 large yellow onion, diced
- 4 large carrots, cut into chunks
- 3 celery stalks, chopped
- 4 cups beef broth
- 1 cup red wine
- 2 TBL tomato paste
- 2 sprigs fresh thyme
- 2 bay leaves
- 1.5 pounds Yukon Gold potatoes, quartered

## Instructions

1. Cut beef into 2-inch chunks and pat dry. Season with salt and pepper, then toss with flour.
2. Heat oil in a heavy Dutch oven over medium-high heat. Brown beef on all \
sides, working in batches.
3. Remove beef and set aside. Reduce heat to medium and add onions to the pot.
4. Cook onions until softened, about 5 minutes. Add tomato paste and cook 1 minute more.
5. Add wine, scraping up any browned bits. Return beef to pot with broth, thyme, and bay leaves.
6. Bring to a boil, then reduce heat to low, cover, and simmer 1 hour.
7. Add carrots, celery, and potatoes. Continue simmering covered until beef \
is tender, about 1 hour more.
8. Remove bay leaves and thyme stems. Adjust seasoning with salt and pepper.
9. Serve hot with crusty bread.

## Notes

- Can be made 1 day ahead and reheated
- Freezes well for up to 3 months

**Tags:** dinner, comfort-food, winter, make-ahead, freezer-friendly
""",
    "invalid_markdown": """# Incomplete Recipe

This markdown is missing required sections and has formatting issues.

## Ingredients
- flour (no amount specified)
-

## Instructions
1. Do something
2.

**Category:**
**Servings:** not a number
""",
}

# Sample YAML recipe data for direct testing
SAMPLE_YAML_CONTENT = {
    "pancakes": {
        "title": "Perfect Pancakes",
        "category": "Breakfast",
        "description": "Fluffy buttermilk pancakes that are perfect for weekend mornings",
        "prep_time_minutes": 10,
        "cook_time_minutes": 15,
        "servings": 4,
        "difficulty": "Easy",
        "ingredients": [
            {
                "ingredient": "all-purpose flour",
                "amount": 2.0,
                "unit": "cups",
                "weight_grams": 240,
                "purpose": "base",
            },
            {
                "ingredient": "granulated sugar",
                "amount": 2.0,
                "unit": "TBL",
                "weight_grams": 25,
                "purpose": "sweetening",
            },
        ],
        "instructions": [
            "In a large bowl, whisk together flour, sugar, baking powder, and salt.",
            "Heat a griddle or large skillet over medium heat.",
        ],
        "notes": ["Don't overmix the batter"],
        "tags": ["breakfast", "pancakes"],
        "source": "Test Recipe",
    }
}


def get_sample_recipe(recipe_name: str) -> Recipe:
    """Get a sample recipe by name.

    Args:
        recipe_name: Name of the recipe to retrieve

    Returns:
        Recipe object

    Raises:
        KeyError: If recipe name not found
    """
    if recipe_name not in ALL_SAMPLE_RECIPES:
        raise KeyError(f"Sample recipe '{recipe_name}' not found. Available: {list(ALL_SAMPLE_RECIPES.keys())}")

    return ALL_SAMPLE_RECIPES[recipe_name]


def get_sample_markdown(recipe_name: str) -> str:
    """Get sample markdown content by recipe name.

    Args:
        recipe_name: Name of the recipe markdown to retrieve

    Returns:
        Markdown content as string
    """
    if recipe_name not in SAMPLE_MARKDOWN_CONTENT:
        raise KeyError(f"Sample markdown '{recipe_name}' not found. Available: {list(SAMPLE_MARKDOWN_CONTENT.keys())}")

    return SAMPLE_MARKDOWN_CONTENT[recipe_name]


def get_sample_yaml_data(recipe_name: str) -> dict:
    """Get sample YAML data by recipe name.

    Args:
        recipe_name: Name of the recipe YAML to retrieve

    Returns:
        YAML data as dictionary
    """
    if recipe_name not in SAMPLE_YAML_CONTENT:
        raise KeyError(f"Sample YAML '{recipe_name}' not found. Available: {list(SAMPLE_YAML_CONTENT.keys())}")

    return SAMPLE_YAML_CONTENT[recipe_name]


def create_test_recipe_variations() -> list[Recipe]:
    """Create variations of test recipes for parameterized testing.

    Returns:
        List of recipe variations
    """
    variations = []

    # Different categories
    categories = [
        "Breakfast",
        "Meat",
        "Dessert",
        "Vegetarian",
        "Seafood",
        "Appetizer",
        "Soup",
        "Salad",
        "Side",
        "Other",
    ]
    for i, category in enumerate(categories):
        recipe = Recipe(
            title=f"Test Recipe {i + 1}",
            category=category,
            ingredients=[Ingredient(ingredient="test ingredient", amount=1.0, unit="cup")],
            instructions=[f"Test instruction for {category} recipe"],
            servings=4,
        )
        variations.append(recipe)

    # Different difficulties
    difficulties = ["Easy", "Medium", "Hard"]
    for _i, difficulty in enumerate(difficulties):
        recipe = Recipe(
            title=f"Difficulty Test {difficulty}",
            category="Other",
            difficulty=difficulty,
            ingredients=[Ingredient(ingredient="ingredient", amount=1.0, unit="unit")],
            instructions=[f"Test instruction with {difficulty} difficulty"],
            servings=2,
        )
        variations.append(recipe)

    return variations
