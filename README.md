# Fantasy Football Data Modeling

The beginnings of a framework to run ML models on large amounts of fantasy football data, for the purpose of evaluating player scoring potential.

## Usage

Tested with Python 3.5 and up. The recommended way to run this is in your own script using a Python virtual environment:

    pip install virtualenv
    virtualenv --python=/path/to/python/interpreter env
    source env/bin/activate
    pip install -r requirements.txt
    python {script call}

> **NOTE: Project is a work-in-progress and not guaranteed to run smoothly at this point**

## Data Sources

See `ff_data/data.py`.

The framework currently supports raw scraping from Pro Football Reference, adhering to all PFF guidelines and rate limits. It includes all available player profile data, as well as season logs and individual game logs going back an arbitrary number of years. The scraper focuses only on fantasy-relevant players for each given year to bump efficiency.

More data sources and features coming soon.

## Models

See `ff_data/models.py`.

There are base sklearn-centric implementations for Decision Tree Regression as well as XGBoost gradient-boosted Decision Tree Regression ensembles. XGBoost hyperparamater optimization can be run via GridSearch with repeated k-fold cross-validation. The framework also supports train-test splits and model result assessment.

More models coming soon.

## Notes on how to model fantasy football data

- After experimenting with several kinds of models, it seems decision tree is the most effective base learner when looking at season-level data (e.g. projecting player scoring potential over the course of a full season). Naturally, random forest and gradient-boosted models are much stronger than individual trees.
- Tree structures allow for grouping players together based on feature values. This can be valuable for making pure regressive scoring predictions, but also for providing other forms of statistical context to a player. For example, we can use gradient-boosted tree sequence to generate a large number of trees. For each node/leaf in each tree, a player is grouped with other similar players - in the aggregate, these groupings can give us input into a player's range of scoring outcomes (e.g. worst-case scenario or best-case scenario).
- Decision trees also might be useful for creating "factor" models that measure statistically significant feature values. Tree splits inherently identify meaningful feature values. This can help us answer questions like "What is the optimal height/weight for a running back?" There are conventional answer to this question, but tree structures give us tools to quantify it at a deeper level using real data.
- Feature engineering is paramount for projecting real-world NFL football outcomes. It is incredibly difficult to create an accurate learning model without some very creative features. This reality is difficult to overcome for 2 reasons. First, it requires deep understanding of the game as well as how the game has changed over time. Second, it creates a burden to unearth data that is often non-public, expensive, fragmented, unstructured, or otherwise hard to source, clean, or model. We simply cannot acquire all the data we need by scraping an online source like PFF(although PFF gives us a very good starting point).
- On-field NFL player performance can typically be assessed in 3 dimensions:
  - Individual player ability
    - Example: draft capital
  - Team roster
    - Example: positional salary cap %
  - Coaching/system
    - Example: coach winning %
  - It is challening to isolate these dimensions - most attributes operate on multiple levels. For example, a player's draft capital may indicate a player's overall potential, but it also represents a team's investment in a given player. Each aspect can impact the model in different ways, particularly if a player moves on to a new team after being drafted elsewhere.
- There is some promise in predicting "opportunity" and/or underlying statistics instead of predicting direct fantasy scoring. Rather than modeling total fantasy points for a season, we can model something like opportunities per game or expected number of games played. Granularized predictions can produce more resilient models.
- Injuries are not easy to account for because of the vast spectrum of injury type and severity. Individual players can also respond differently to the same injury. Injuries can have massive impact on a player's fantasy value from season to season, so ignoring injury data is not a good option.
  - Maybe it's possible to engineer a proxy feature like "missed game probability" that can be incorpoated into the model.
- Rookie players are particularly hard to model because of the lack of NFL statistical history. While XGBoost can handle undefined values by optimizing tree splits, we probably need a separate model enitrely with rookie-specific features.
