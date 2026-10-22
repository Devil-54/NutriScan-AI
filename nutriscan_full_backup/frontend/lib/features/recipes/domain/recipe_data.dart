class Recipe {
  const Recipe({
    required this.name,
    required this.description,
    required this.category,
    required this.ingredients,
    required this.steps,
    required this.calories,
    required this.protein,
    required this.carbohydrates,
    required this.fat,
    required this.fibre,
  });

  final String name;
  final String description;
  final String category;
  final List<String> ingredients;
  final List<String> steps;
  final int calories;
  final int protein;
  final int carbohydrates;
  final int fat;
  final int fibre;
}

const recipes = [
  Recipe(name: 'Vegetable Oats Bowl', description: 'Creamy oats with colourful vegetables and warming spices.', category: 'Breakfast', ingredients: ['Rolled oats', 'Carrot', 'Green peas', 'Onion', 'Milk or water', 'Cumin and pepper'], steps: ['Sauté onion, carrot and peas with cumin.', 'Add oats and milk or water.', 'Cook until creamy; season with pepper.'], calories: 310, protein: 11, carbohydrates: 50, fat: 8, fibre: 8),
  Recipe(name: 'Vegetable Poha', description: 'Light flattened-rice breakfast with peas, potato and lemon.', category: 'Breakfast', ingredients: ['Poha', 'Onion', 'Potato', 'Green peas', 'Mustard seeds', 'Lemon'], steps: ['Rinse poha briefly and set aside.', 'Temper mustard seeds; cook onion, potato and peas.', 'Fold in poha and finish with lemon.'], calories: 280, protein: 6, carbohydrates: 48, fat: 7, fibre: 5),
  Recipe(name: 'Moong Dal Chilla', description: 'Protein-rich savoury pancakes made with soaked moong dal.', category: 'Breakfast', ingredients: ['Soaked moong dal', 'Onion', 'Tomato', 'Coriander', 'Green chilli', 'Oil'], steps: ['Blend soaked dal into a smooth batter.', 'Mix in chopped vegetables and seasoning.', 'Cook thin chillas on a lightly oiled pan.'], calories: 300, protein: 16, carbohydrates: 38, fat: 9, fibre: 7),
  Recipe(name: 'Idli with Sambar', description: 'Steamed rice-lentil cakes served with vegetable lentil stew.', category: 'Breakfast', ingredients: ['Idli batter', 'Toor dal', 'Mixed vegetables', 'Sambar powder', 'Tamarind', 'Curry leaves'], steps: ['Steam idlis until set.', 'Cook dal and vegetables until tender.', 'Season with tamarind, sambar powder and curry leaves.'], calories: 340, protein: 12, carbohydrates: 62, fat: 5, fibre: 8),
  Recipe(name: 'Dal with Brown Rice and Salad', description: 'Comforting lentils with whole-grain rice and a fresh salad.', category: 'Lunch', ingredients: ['Brown rice', 'Toor dal', 'Tomato', 'Cucumber', 'Carrot', 'Cumin'], steps: ['Cook brown rice until tender.', 'Simmer dal with tomato and spices.', 'Serve with a cucumber and carrot salad.'], calories: 460, protein: 18, carbohydrates: 78, fat: 8, fibre: 13),
  Recipe(name: 'Vegetable Khichdi', description: 'One-pot rice and lentil meal with seasonal vegetables.', category: 'Lunch', ingredients: ['Rice', 'Moong dal', 'Carrot', 'Beans', 'Green peas', 'Turmeric'], steps: ['Rinse rice and dal.', 'Add vegetables, turmeric and water.', 'Pressure cook until soft and comforting.'], calories: 390, protein: 15, carbohydrates: 66, fat: 8, fibre: 10),
  Recipe(name: 'Paneer/Tofu Salad Bowl', description: 'Fresh salad bowl with grilled paneer or tofu and legumes.', category: 'Lunch', ingredients: ['Paneer or tofu', 'Lettuce', 'Cucumber', 'Tomato', 'Chickpeas', 'Lemon dressing'], steps: ['Season and grill paneer or tofu.', 'Combine vegetables and chickpeas.', 'Top with paneer or tofu and lemon dressing.'], calories: 410, protein: 24, carbohydrates: 30, fat: 22, fibre: 10),
  Recipe(name: 'Roti with Dal and Vegetables', description: 'Balanced everyday plate with whole-wheat roti, dal and sabzi.', category: 'Lunch', ingredients: ['Whole-wheat flour', 'Moong dal', 'Seasonal vegetables', 'Tomato', 'Cumin', 'Turmeric'], steps: ['Make and cook whole-wheat rotis.', 'Simmer dal with tomato and spices.', 'Stir-fry vegetables and serve together.'], calories: 450, protein: 19, carbohydrates: 72, fat: 10, fibre: 14),
  Recipe(name: 'Vegetable Soup with Roti', description: 'Hearty mixed-vegetable soup with soft whole-wheat roti.', category: 'Dinner', ingredients: ['Mixed vegetables', 'Tomato', 'Vegetable stock', 'Whole-wheat flour', 'Garlic', 'Herbs'], steps: ['Sauté garlic and vegetables.', 'Add stock and simmer until tender.', 'Blend partly if desired; serve with roti.'], calories: 330, protein: 12, carbohydrates: 55, fat: 7, fibre: 11),
  Recipe(name: 'Moong Dal Khichdi', description: 'Gentle, easy-to-digest rice and moong dal comfort meal.', category: 'Dinner', ingredients: ['Moong dal', 'Rice', 'Ginger', 'Cumin', 'Turmeric', 'Ghee'], steps: ['Rinse rice and moong dal.', 'Cook with ginger, cumin, turmeric and water.', 'Finish with a small spoon of ghee.'], calories: 370, protein: 16, carbohydrates: 64, fat: 8, fibre: 9),
  Recipe(name: 'Paneer/Tofu Vegetable Bowl', description: 'Warm bowl of roasted vegetables with paneer or tofu.', category: 'Dinner', ingredients: ['Paneer or tofu', 'Broccoli', 'Bell pepper', 'Carrot', 'Brown rice', 'Sesame seeds'], steps: ['Roast vegetables until tender.', 'Pan-sear paneer or tofu.', 'Layer with brown rice and sprinkle sesame seeds.'], calories: 430, protein: 25, carbohydrates: 45, fat: 18, fibre: 10),
  Recipe(name: 'Grilled Vegetable Wrap', description: 'Whole-wheat wrap packed with grilled vegetables and hummus.', category: 'Dinner', ingredients: ['Whole-wheat wrap', 'Bell pepper', 'Zucchini', 'Onion', 'Hummus', 'Lettuce'], steps: ['Grill the sliced vegetables.', 'Spread hummus over the wrap.', 'Add vegetables and lettuce, then roll tightly.'], calories: 380, protein: 14, carbohydrates: 58, fat: 12, fibre: 12),
];
