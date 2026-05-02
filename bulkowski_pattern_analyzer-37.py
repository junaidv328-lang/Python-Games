"""
=============================================================================
 BULKOWSKI CHART PATTERN ANALYZER
 Based on: Encyclopedia of Chart Patterns (2nd Ed.) - Thomas N. Bulkowski
 Author  : For Junaid / VAR Fisheries / FishyBiz Research Tools
 Version : 1.0
 Usage   : Run in Spyder. Follow the menu to upload CSV and analyze patterns.
=============================================================================

HOW TO USE:
  1. Run this file in Spyder (press F5 or click Run)
  2. The app opens a GUI window
  3. Click "Load Chart Data (CSV)" and select your OHLCV CSV file
  4. The app detects patterns automatically
  5. Each matched pattern shows Bulkowski's statistics + trading plan

CSV FORMAT REQUIRED:
  Your CSV must have columns: Date, Open, High, Low, Close, Volume
  (Column names are case-insensitive)

INSTALLATION (run once in Spyder console):
  pip install pandas numpy matplotlib scipy tkinter
"""

# ── IMPORTS ──────────────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from scipy.signal import argrelextrema
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────────────────
#  BULKOWSKI DATABASE — All 53 Chart Patterns with Statistics
#  Source: Encyclopedia of Chart Patterns, 2nd Ed., Thomas N. Bulkowski, 2005
# ─────────────────────────────────────────────────────────────────────────────

PATTERNS_DB = {

    # ── REVERSAL PATTERNS — BOTTOMS ──────────────────────────────────────────

    "Double Bottom (Adam & Adam)": {
        "type": "reversal", "direction": "bullish",
        "category": "Double Bottoms",
        "description": "Two sharp V-shaped bottoms at approximately the same price level. Both bottoms are narrow (Adam type). Classic bullish reversal pattern.",
        "identification": [
            "Two distinct lows separated by a moderate peak",
            "Both lows are sharp/narrow (Adam type = pointed V)",
            "Second low within 3–4% of the first low",
            "Valley between the two lows must rise at least 10%",
            "Confirm with breakout above the valley peak (neckline)",
        ],
        "stats": {
            "bull_market": {
                "avg_rise": "35%",
                "breakeven_failure_rate": "6%",
                "throwback_rate": "64%",
                "avg_throwback_days": "11 days",
                "performance_rank": "Good",
                "samples": 584,
            },
            "bear_market": {
                "avg_rise": "20%",
                "breakeven_failure_rate": "15%",
                "throwback_rate": "55%",
                "avg_throwback_days": "10 days",
                "performance_rank": "Fair",
                "samples": 223,
            }
        },
        "measure_rule": "Add height of pattern (from lowest low to neckline) to the neckline breakout price for the target.",
        "target_reliability": "68% in bull markets",
        "trading_plan": {
            "entry": "Enter long 1 tick above the neckline (the peak between the two bottoms) on a confirmed daily close above it.",
            "stop": "Place stop 1 tick below the lower of the two bottoms. Risk = neckline to stop distance.",
            "target_1": "Measure the height from the lowest low to the neckline. Add this to the neckline breakout price.",
            "target_2": "If breakout shows strong volume: extend target to 150% of pattern height.",
            "exit_rule": "If a throwback occurs (price returns to neckline): hold if close is above neckline. Exit if close below.",
            "avoid": "Skip if neckline is near a major resistance level. Skip if second bottom is more than 4% below first.",
        },
        "best_performance": [
            "Bull market, upward breakout — highest reliability",
            "Pattern height above the 1-month median performs better",
            "Low in the yearly price range (lower third) = best gains",
            "Breakout on above-average volume = stronger move",
        ],
        "color": "#2ecc71",
    },

    "Double Bottom (Eve & Eve)": {
        "type": "reversal", "direction": "bullish",
        "category": "Double Bottoms",
        "description": "Two rounded/wide U-shaped bottoms at approximately the same level. Both bottoms are broad (Eve type). Very common and reliable.",
        "identification": [
            "Two distinct lows — both wide/rounded (Eve = broad U shape)",
            "Second low within 3–4% of first low price",
            "Peak between bottoms rises at least 10%",
            "Eve bottoms show more day-to-day price variation than Adam",
            "Breakout: daily close above the peak between the two bottoms",
        ],
        "stats": {
            "bull_market": {
                "avg_rise": "40%",
                "breakeven_failure_rate": "5%",
                "throwback_rate": "59%",
                "avg_throwback_days": "11 days",
                "performance_rank": "Excellent",
                "samples": 776,
            },
            "bear_market": {
                "avg_rise": "23%",
                "breakeven_failure_rate": "11%",
                "throwback_rate": "54%",
                "avg_throwback_days": "10 days",
                "performance_rank": "Good",
                "samples": 297,
            }
        },
        "measure_rule": "Height of pattern (lowest low to neckline) + neckline price.",
        "target_reliability": "72% in bull markets",
        "trading_plan": {
            "entry": "Enter long on close above neckline (peak between two bottoms).",
            "stop": "Below the lower of the two Eve bottoms.",
            "target_1": "Neckline price + pattern height.",
            "target_2": "If volume expansion on breakout: 150% of pattern height target.",
            "exit_rule": "Scale out 50% at T1. Hold 50% with trailing stop under each new swing low.",
            "avoid": "Overhead resistance nearby (within 5% of target). High ADX suggesting already exhausted move.",
        },
        "best_performance": [
            "Best performer among all double bottom variants",
            "Bull market significantly outperforms bear market",
            "Higher pattern = better performance (taller = more reliable)",
            "Breakout near yearly low = best percentage gains",
        ],
        "color": "#27ae60",
    },

    "Double Bottom (Adam & Eve)": {
        "type": "reversal", "direction": "bullish",
        "category": "Double Bottoms",
        "description": "First bottom is sharp (Adam), second is broad (Eve). Mixed pattern — moderately reliable.",
        "identification": [
            "First bottom: sharp V-shape (narrow, pointed)",
            "Second bottom: broad U-shape (rounded, wider)",
            "Second bottom at approximately same price level ±4%",
            "Valley peak must be clearly defined",
        ],
        "stats": {
            "bull_market": {
                "avg_rise": "37%",
                "breakeven_failure_rate": "7%",
                "throwback_rate": "61%",
                "avg_throwback_days": "11 days",
                "performance_rank": "Good",
                "samples": 521,
            },
            "bear_market": {
                "avg_rise": "22%",
                "breakeven_failure_rate": "12%",
                "throwback_rate": "52%",
                "avg_throwback_days": "10 days",
                "performance_rank": "Fair",
                "samples": 198,
            }
        },
        "measure_rule": "Standard: pattern height added to neckline breakout price.",
        "target_reliability": "70% bull markets",
        "trading_plan": {
            "entry": "Close above neckline breakout.",
            "stop": "Below lower of the two bottoms.",
            "target_1": "Pattern height added to neckline.",
            "target_2": "Prior swing high if closer than calculated target.",
            "exit_rule": "Hold through throwback if neckline holds. Exit on daily close below neckline.",
            "avoid": "If the two bottoms differ by more than 5% in price.",
        },
        "best_performance": [
            "Bull markets perform substantially better",
            "Tall patterns outperform short ones",
            "Breakout near yearly low gives best results",
        ],
        "color": "#1abc9c",
    },

    "Triple Bottom": {
        "type": "reversal", "direction": "bullish",
        "category": "Triple Patterns",
        "description": "Three consecutive lows at approximately the same price level, forming a strong support zone. Reliable reversal pattern.",
        "identification": [
            "Three distinct lows at approximately the same price (within 3%)",
            "Two peaks between the three lows — both neckline points",
            "Each low must be a clear swing low (not just a minor dip)",
            "Pattern should span at least 3–4 weeks",
            "Breakout: close above the higher of the two peaks",
        ],
        "stats": {
            "bull_market": {
                "avg_rise": "37%",
                "breakeven_failure_rate": "4%",
                "throwback_rate": "64%",
                "avg_throwback_days": "11 days",
                "performance_rank": "Excellent",
                "samples": 211,
            },
            "bear_market": {
                "avg_rise": "22%",
                "breakeven_failure_rate": "14%",
                "throwback_rate": "55%",
                "avg_throwback_days": "10 days",
                "performance_rank": "Good",
                "samples": 88,
            }
        },
        "measure_rule": "Height from lowest low to highest neckline, added to neckline breakout price.",
        "target_reliability": "66% bull markets",
        "trading_plan": {
            "entry": "Close above the higher neckline of the two peaks.",
            "stop": "Below the lowest of the three bottoms.",
            "target_1": "Pattern height + breakout price.",
            "target_2": "Prior resistance level above the breakout.",
            "exit_rule": "Throwback to neckline: hold if neckline holds. Trail stop after T1.",
            "avoid": "If peaks vary by more than 4% in height — pattern may be unreliable.",
        },
        "best_performance": [
            "Very low failure rate — one of the most reliable bullish patterns",
            "Bull markets far outperform bear markets",
            "Patterns with equal three lows (within 1%) most reliable",
        ],
        "color": "#16a085",
    },

    "Head-and-Shoulders Bottom": {
        "type": "reversal", "direction": "bullish",
        "category": "Head and Shoulders",
        "description": "Three lows where the center (head) is lower than the two shoulders. Classic major reversal pattern.",
        "identification": [
            "Three lows: left shoulder, head (deepest), right shoulder",
            "Head is clearly lower than both shoulders",
            "Right shoulder should be at similar height to left shoulder (±5%)",
            "Neckline drawn across the tops of the two peaks between shoulders and head",
            "Confirm: daily close above neckline with volume expansion",
        ],
        "stats": {
            "bull_market": {
                "avg_rise": "38%",
                "breakeven_failure_rate": "3%",
                "throwback_rate": "45%",
                "avg_throwback_days": "11 days",
                "performance_rank": "Excellent",
                "samples": 733,
            },
            "bear_market": {
                "avg_rise": "24%",
                "breakeven_failure_rate": "8%",
                "throwback_rate": "40%",
                "avg_throwback_days": "10 days",
                "performance_rank": "Good",
                "samples": 279,
            }
        },
        "measure_rule": "Measure from head low to neckline. Add to neckline breakout price.",
        "target_reliability": "55–60% (conservative but reliable entry with tight stops)",
        "trading_plan": {
            "entry": "Daily close above neckline. Aggressive: buy intraday on neckline touch.",
            "stop": "Below the right shoulder low. OR below the head for wider stop.",
            "target_1": "Head-to-neckline distance projected upward from neckline.",
            "target_2": "Prior swing highs above the pattern.",
            "exit_rule": "If throwback to neckline: hold if neckline is support. Exit daily close below neckline.",
            "avoid": "Slanting necklines (more than 15° slope) = less reliable. Avoid if right shoulder is significantly lower than left.",
        },
        "best_performance": [
            "One of the highest reliability patterns with 3% failure rate in bull markets",
            "Lower throwback rate than double bottoms = cleaner entries",
            "Bull market performance dramatically better",
            "Horizontal neckline outperforms slanted",
        ],
        "color": "#3498db",
    },

    "Cup with Handle": {
        "type": "reversal", "direction": "bullish",
        "category": "Cup Patterns",
        "description": "U-shaped cup (rounding bottom) followed by a small handle (slight downward drift). Popularized by William O'Neil. Continuation/reversal pattern.",
        "identification": [
            "Cup: U-shaped rounding bottom, NOT a V-shape",
            "Cup depth: typically 15–30% from rim to cup bottom",
            "Handle: small pullback in the upper third of the cup (5–15% decline)",
            "Handle should drift down along light volume",
            "Breakout: close above the rim of the cup (prior high)",
        ],
        "stats": {
            "bull_market": {
                "avg_rise": "34%",
                "breakeven_failure_rate": "5%",
                "throwback_rate": "52%",
                "avg_throwback_days": "11 days",
                "performance_rank": "Good",
                "samples": 428,
            },
            "bear_market": {
                "avg_rise": "22%",
                "breakeven_failure_rate": "13%",
                "throwback_rate": "47%",
                "avg_throwback_days": "11 days",
                "performance_rank": "Fair",
                "samples": 147,
            }
        },
        "measure_rule": "Cup depth projected upward from the breakout (rim) price.",
        "target_reliability": "58% in bull markets",
        "trading_plan": {
            "entry": "Close above the prior rim high (cup lip). Ideally with heavy volume.",
            "stop": "Below the handle low.",
            "target_1": "Breakout price + cup depth.",
            "target_2": "Prior all-time high if cup forms in a pullback.",
            "exit_rule": "Throwback to rim level: hold if rim holds as support. Exit on close below rim.",
            "avoid": "V-shaped cup (too steep). Handle that drops more than half the cup depth. Handle that drifts up instead of down.",
        },
        "best_performance": [
            "Bull markets significantly better than bear markets",
            "Cups with symmetrical shape outperform asymmetric cups",
            "Breakout on heavy volume (2x average) shows best performance",
            "Shorter cup duration (4–7 weeks) outperforms longer cups",
        ],
        "color": "#9b59b6",
    },

    "Rounding Bottom (Saucer)": {
        "type": "reversal", "direction": "bullish",
        "category": "Rounding Patterns",
        "description": "Gradual, smooth U-shaped curve over many weeks or months. Represents a long-term shift from selling to buying pressure.",
        "identification": [
            "Slow, gradual decline followed by slow, gradual rise",
            "Price action traces a smooth curved arc (NOT jagged)",
            "Volume typically decreases at the bottom and increases on the way up",
            "Pattern usually spans 7 weeks to several months",
            "Breakout: close above prior high before the rounding started",
        ],
        "stats": {
            "bull_market": {
                "avg_rise": "43%",
                "breakeven_failure_rate": "5%",
                "throwback_rate": "33%",
                "avg_throwback_days": "11 days",
                "performance_rank": "Excellent",
                "samples": 198,
            },
            "bear_market": {
                "avg_rise": "31%",
                "breakeven_failure_rate": "8%",
                "throwback_rate": "29%",
                "avg_throwback_days": "10 days",
                "performance_rank": "Good",
                "samples": 74,
            }
        },
        "measure_rule": "Depth of the rounding bottom added to the right lip (breakout price).",
        "target_reliability": "61% bull markets",
        "trading_plan": {
            "entry": "Close above the right rim (prior high that preceded the rounding). Very low throwback rate — this is clean.",
            "stop": "Below the low of the rounding bottom.",
            "target_1": "Pattern depth + breakout price.",
            "target_2": "Measured move using prior trend leg.",
            "exit_rule": "Lowest throwback rate of major patterns — hold aggressively through the first pullback.",
            "avoid": "Pattern with too many jagged days (should be smooth). Avoid if pattern is less than 7 bars wide.",
        },
        "best_performance": [
            "Highest average rise among common bullish patterns (43% in bull)",
            "Very low throwback rate = clean holds with minimal stress",
            "Works especially well at major market bottoms",
        ],
        "color": "#e67e22",
    },

    "Bump-and-Run Reversal Bottom": {
        "type": "reversal", "direction": "bullish",
        "category": "Bump-and-Run",
        "description": "A declining lead-in trendline followed by a downward spike (bump) that overshoots the lead-in angle, then reverses (run). Bottom reversal.",
        "identification": [
            "Lead-in phase: gentle downtrend with consistent slope",
            "Bump phase: price declines sharply below the lead-in trendline (typically at 45°+ steeper)",
            "Bump height: at least 2x the lead-in height from trendline",
            "Run phase: price reverses back above the lead-in trendline",
            "Volume spike during the bump phase",
        ],
        "stats": {
            "bull_market": {
                "avg_rise": "37%",
                "breakeven_failure_rate": "5%",
                "throwback_rate": "62%",
                "avg_throwback_days": "11 days",
                "performance_rank": "Good",
                "samples": 182,
            },
            "bear_market": {
                "avg_rise": "27%",
                "breakeven_failure_rate": "11%",
                "throwback_rate": "54%",
                "avg_throwback_days": "10 days",
                "performance_rank": "Fair",
                "samples": 67,
            }
        },
        "measure_rule": "Bump height (from lead-in trendline to bump low) projected upward from breakout.",
        "target_reliability": "63%",
        "trading_plan": {
            "entry": "Close above the lead-in trendline extended to the right (the 'run' breakout).",
            "stop": "Below the bump low.",
            "target_1": "Bump height projected from the breakout point.",
            "target_2": "Prior resistance before the lead-in decline.",
            "exit_rule": "If throwback to trendline: hold if trendline acts as support.",
            "avoid": "If the bump is not clearly steeper than the lead-in (must be a clear angle change).",
        },
        "best_performance": [
            "Works best when bump is 2–3x the lead-in height",
            "Strong volume on the reversal from the bump low improves performance",
            "Bull markets substantially outperform",
        ],
        "color": "#f39c12",
    },

    # ── REVERSAL PATTERNS — TOPS ──────────────────────────────────────────────

    "Double Top (Eve & Eve)": {
        "type": "reversal", "direction": "bearish",
        "category": "Double Tops",
        "description": "Two broad/rounded tops at approximately the same price level. Both peaks are Eve-type (wide, rounded). Most reliable double top variant.",
        "identification": [
            "Two distinct highs — both wide/rounded (Eve type = broad, curved)",
            "Second top within 3–4% of first top price",
            "Valley between tops declines at least 10%",
            "Breakout: daily close below the valley low (neckline)",
        ],
        "stats": {
            "bull_market": {
                "avg_decline": "18%",
                "breakeven_failure_rate": "11%",
                "pullback_rate": "59%",
                "avg_pullback_days": "11 days",
                "performance_rank": "Good",
                "samples": 589,
            },
            "bear_market": {
                "avg_decline": "24%",
                "breakeven_failure_rate": "8%",
                "pullback_rate": "52%",
                "avg_pullback_days": "10 days",
                "performance_rank": "Excellent",
                "samples": 213,
            }
        },
        "measure_rule": "Pattern height (highest top to neckline) subtracted from neckline breakout price.",
        "target_reliability": "68% bear markets",
        "trading_plan": {
            "entry": "Close below neckline (the valley low between the two tops).",
            "stop": "Above the lower of the two tops.",
            "target_1": "Neckline price minus pattern height.",
            "target_2": "Major support level below.",
            "exit_rule": "If pullback occurs (price returns to neckline): hold if neckline acts as resistance. Exit on close above neckline.",
            "avoid": "Skip if support is within 5% of target. Skip if second top is more than 4% above first.",
        },
        "best_performance": [
            "Best performer among double top variants",
            "Bear markets show highest reliability for this pattern",
            "Taller patterns (height above median) perform better",
            "Breakout near yearly high gives best decline percentage",
        ],
        "color": "#e74c3c",
    },

    "Double Top (Adam & Adam)": {
        "type": "reversal", "direction": "bearish",
        "category": "Double Tops",
        "description": "Two sharp V-shaped tops at approximately the same price. Both peaks are Adam-type (narrow, pointed spikes).",
        "identification": [
            "Two distinct highs — both narrow/sharp (Adam type = pointed spikes)",
            "Second top within 3–4% of first top",
            "Valley between tops shows clear decline (10% minimum)",
            "Breakout: close below valley low",
        ],
        "stats": {
            "bull_market": {
                "avg_decline": "15%",
                "breakeven_failure_rate": "15%",
                "pullback_rate": "62%",
                "avg_pullback_days": "11 days",
                "performance_rank": "Fair",
                "samples": 458,
            },
            "bear_market": {
                "avg_decline": "20%",
                "breakeven_failure_rate": "10%",
                "pullback_rate": "55%",
                "avg_pullback_days": "10 days",
                "performance_rank": "Good",
                "samples": 178,
            }
        },
        "measure_rule": "Pattern height subtracted from neckline breakout price.",
        "target_reliability": "60% bear markets",
        "trading_plan": {
            "entry": "Close below neckline.",
            "stop": "Above higher of the two tops.",
            "target_1": "Neckline minus pattern height.",
            "target_2": "Major support below.",
            "exit_rule": "Pullback to neckline: hold if neckline resistance holds. Exit close above neckline.",
            "avoid": "High pullback rate (62% in bull markets) — be prepared for pullback management.",
        },
        "best_performance": [
            "Bear markets outperform bull markets significantly",
            "Pattern fails more often in bull markets (15% failure rate)",
        ],
        "color": "#c0392b",
    },

    "Head-and-Shoulders Top": {
        "type": "reversal", "direction": "bearish",
        "category": "Head and Shoulders",
        "description": "Three peaks where the center (head) is highest. The most famous bearish reversal pattern in technical analysis.",
        "identification": [
            "Three peaks: left shoulder, head (highest), right shoulder",
            "Head is clearly higher than both shoulders",
            "Right shoulder approximately same height as left (±5%)",
            "Neckline drawn across the lows between peaks",
            "Confirm: daily close below neckline (ideally with volume expansion)",
        ],
        "stats": {
            "bull_market": {
                "avg_decline": "22%",
                "breakeven_failure_rate": "4%",
                "pullback_rate": "45%",
                "avg_pullback_days": "11 days",
                "performance_rank": "Excellent",
                "samples": 1042,
            },
            "bear_market": {
                "avg_decline": "29%",
                "breakeven_failure_rate": "3%",
                "pullback_rate": "38%",
                "avg_pullback_days": "10 days",
                "performance_rank": "Excellent",
                "samples": 419,
            }
        },
        "measure_rule": "Height from head high to neckline, subtracted from neckline breakout price.",
        "target_reliability": "50–55% (conservative measure rule, pattern is very reliable for direction)",
        "trading_plan": {
            "entry": "Close below neckline. OR short on pullback to neckline (if pullback occurs after initial breakdown).",
            "stop": "Above right shoulder high.",
            "target_1": "Neckline price minus head-to-neckline height.",
            "target_2": "Major support levels below.",
            "exit_rule": "Lower pullback rate than most = less interference. Trail stop below each lower high.",
            "avoid": "Sloping neckline (downward sloping is bearish but harder to trade). Right shoulder much higher than left = weaker pattern.",
        },
        "best_performance": [
            "Lowest failure rate among bearish patterns (3–4%)",
            "Works in both bull and bear markets — versatile",
            "Bear market gives dramatically better percentage decline",
            "Horizontal neckline outperforms slanting",
            "Volume should diminish during right shoulder formation",
        ],
        "color": "#8e44ad",
    },

    "Triple Top": {
        "type": "reversal", "direction": "bearish",
        "category": "Triple Patterns",
        "description": "Three consecutive highs at approximately the same price, forming a strong resistance ceiling. Reliable bearish reversal.",
        "identification": [
            "Three distinct highs at approximately the same price (within 3%)",
            "Two valleys between the three peaks",
            "Each high must be a clear swing high",
            "Pattern spans at least 3–4 weeks",
            "Breakout: close below the lower of the two valleys",
        ],
        "stats": {
            "bull_market": {
                "avg_decline": "19%",
                "breakeven_failure_rate": "4%",
                "pullback_rate": "60%",
                "avg_pullback_days": "11 days",
                "performance_rank": "Good",
                "samples": 180,
            },
            "bear_market": {
                "avg_decline": "25%",
                "breakeven_failure_rate": "4%",
                "pullback_rate": "50%",
                "avg_pullback_days": "10 days",
                "performance_rank": "Excellent",
                "samples": 71,
            }
        },
        "measure_rule": "Height from highest top to lowest neckline, subtracted from breakout price.",
        "target_reliability": "64% in bear markets",
        "trading_plan": {
            "entry": "Close below the lower valley (neckline).",
            "stop": "Above the highest of the three tops.",
            "target_1": "Neckline minus pattern height.",
            "target_2": "Prior major support below.",
            "exit_rule": "High pullback rate (60%) — be prepared. Hold if neckline resistance holds on pullback.",
            "avoid": "Peaks that vary by more than 4% in height — less reliable pattern.",
        },
        "best_performance": [
            "Very low failure rate (4%) — high reliability for direction",
            "Bear markets show best performance",
        ],
        "color": "#d35400",
    },

    "Bump-and-Run Reversal Top": {
        "type": "reversal", "direction": "bearish",
        "category": "Bump-and-Run",
        "description": "Rising lead-in trendline followed by a parabolic spike (bump) and reversal (run). Identifies unsustainable price spikes.",
        "identification": [
            "Lead-in: gradual rising trendline, consistent slope",
            "Bump: price surges dramatically above lead-in trendline (at 45°+ steeper angle)",
            "Bump height: at least 2x the lead-in height from trendline",
            "Run: price reverses and breaks back below the lead-in trendline",
            "Volume: typically high during the bump phase",
        ],
        "stats": {
            "bull_market": {
                "avg_decline": "21%",
                "breakeven_failure_rate": "8%",
                "pullback_rate": "40%",
                "avg_pullback_days": "11 days",
                "performance_rank": "Good",
                "samples": 206,
            },
            "bear_market": {
                "avg_decline": "25%",
                "breakeven_failure_rate": "6%",
                "pullback_rate": "35%",
                "avg_pullback_days": "10 days",
                "performance_rank": "Excellent",
                "samples": 82,
            }
        },
        "measure_rule": "Bump height subtracted from the lead-in trendline breakout price.",
        "target_reliability": "65%",
        "trading_plan": {
            "entry": "Short on close below the lead-in trendline (the 'run' starts).",
            "stop": "Above the bump high.",
            "target_1": "Bump height subtracted from breakout price.",
            "target_2": "Start of the lead-in phase (where the gradual rise began).",
            "exit_rule": "Lower pullback rate than most = cleaner short hold.",
            "avoid": "If bump angle is not clearly steeper than lead-in. Need clear angle change.",
        },
        "best_performance": [
            "Low pullback rate = comfortable short holds",
            "Works well in both market conditions",
            "Identifying the bump correctly is the key skill",
        ],
        "color": "#e74c3c",
    },

    # ── CONTINUATION PATTERNS ─────────────────────────────────────────────────

    "Ascending Triangle": {
        "type": "continuation", "direction": "bullish",
        "category": "Triangles",
        "description": "Flat top resistance line with rising bottom trendline. Bullish continuation pattern — buyers are making higher lows while sellers hold at a fixed resistance.",
        "identification": [
            "Top: horizontal resistance line (flat) — two or more peaks at same level",
            "Bottom: upward sloping trendline connecting rising lows",
            "At least two peaks touching the resistance line",
            "At least two higher lows touching the rising trendline",
            "Breakout: ideally upward through the resistance line",
        ],
        "stats": {
            "bull_market": {
                "avg_rise": "35%",
                "breakeven_failure_rate": "13%",
                "throwback_rate": "57%",
                "avg_throwback_days": "11 days",
                "upward_breakout_pct": "70%",
                "performance_rank": "Good",
                "samples": 770,
            },
            "bear_market": {
                "avg_rise": "27%",
                "breakeven_failure_rate": "14%",
                "throwback_rate": "47%",
                "avg_throwback_days": "10 days",
                "upward_breakout_pct": "57%",
                "performance_rank": "Good",
                "samples": 319,
            }
        },
        "measure_rule": "Height of triangle (widest part at the left side) added to breakout price.",
        "target_reliability": "75% in bull markets",
        "trading_plan": {
            "entry": "Close above the flat resistance top line.",
            "stop": "Below the most recent higher low within the triangle.",
            "target_1": "Triangle height added to breakout price.",
            "target_2": "Prior swing high above triangle.",
            "exit_rule": "If throwback to resistance line: hold if line acts as support. Exit on close below.",
            "avoid": "Downward breakouts from ascending triangles underperform — consider not trading downside break. Wide triangles (long duration) can fail more.",
        },
        "best_performance": [
            "Upward breakouts occur 70% of the time in bull markets",
            "High throwback rate (57%) — be prepared but hold through it",
            "Best performance when breakout occurs in lower part of yearly range",
            "Tall patterns outperform short patterns",
        ],
        "color": "#2980b9",
    },

    "Descending Triangle": {
        "type": "continuation", "direction": "bearish",
        "category": "Triangles",
        "description": "Flat bottom support line with falling top trendline. Bearish continuation — sellers making lower highs while buyers hold at fixed support.",
        "identification": [
            "Bottom: horizontal support line — two or more lows at same level",
            "Top: downward sloping trendline connecting falling highs",
            "At least two lows touching support",
            "At least two lower highs touching the falling trendline",
            "Breakout: typically downward through support",
        ],
        "stats": {
            "bull_market": {
                "avg_decline": "16%",
                "breakeven_failure_rate": "16%",
                "pullback_rate": "54%",
                "avg_pullback_days": "11 days",
                "downward_breakout_pct": "64%",
                "performance_rank": "Fair",
                "samples": 722,
            },
            "bear_market": {
                "avg_decline": "21%",
                "breakeven_failure_rate": "11%",
                "pullback_rate": "47%",
                "avg_pullback_days": "10 days",
                "downward_breakout_pct": "72%",
                "performance_rank": "Good",
                "samples": 286,
            }
        },
        "measure_rule": "Triangle height subtracted from breakout price.",
        "target_reliability": "62% bear markets",
        "trading_plan": {
            "entry": "Close below the flat support line.",
            "stop": "Above the most recent lower high within the triangle.",
            "target_1": "Support price minus triangle height.",
            "target_2": "Prior swing low below triangle.",
            "exit_rule": "Pullback to support: hold if support acts as resistance. Exit on close above support.",
            "avoid": "Higher failure rate in bull markets (16%) — wait for bear market context for better reliability.",
        },
        "best_performance": [
            "Bear market context gives much better performance",
            "Lower failure rate in bear markets",
            "Downward breakout occurs 64–72% of the time",
        ],
        "color": "#c0392b",
    },

    "Symmetrical Triangle": {
        "type": "continuation", "direction": "neutral",
        "category": "Triangles",
        "description": "Converging upper and lower trendlines with no clear horizontal bias. Breakout can go either direction but favors the prior trend.",
        "identification": [
            "Upper trendline: falling, connecting lower highs",
            "Lower trendline: rising, connecting higher lows",
            "Both trendlines converge to an apex",
            "At least 2 touches on each trendline",
            "Breakout: close outside either trendline",
        ],
        "stats": {
            "bull_market": {
                "avg_rise": "31%",
                "avg_decline": "17%",
                "breakeven_failure_rate": "11%",
                "throwback_rate": "37%",
                "upward_breakout_pct": "54%",
                "performance_rank": "Good",
                "samples": 1109,
            },
            "bear_market": {
                "avg_rise": "25%",
                "avg_decline": "20%",
                "breakeven_failure_rate": "13%",
                "throwback_rate": "38%",
                "downward_breakout_pct": "57%",
                "performance_rank": "Good",
                "samples": 479,
            }
        },
        "measure_rule": "Triangle height (widest left side) added to/subtracted from breakout price.",
        "target_reliability": "66% bull upward breakout",
        "trading_plan": {
            "entry": "Trade in direction of the prior trend. Enter on breakout close outside the relevant trendline.",
            "stop": "Inside the triangle (opposite trendline area).",
            "target_1": "Triangle height applied to breakout price.",
            "target_2": "Prior swing high (upward) or low (downward).",
            "exit_rule": "Low throwback/pullback rate (37%) = relatively clean holds.",
            "avoid": "Do not predict direction before the breakout occurs. Let the market tell you.",
        },
        "best_performance": [
            "Low throwback rate = one of the cleanest triangles to hold",
            "Follow the breakout direction — do not predict",
            "Tall patterns perform better for upward breakouts",
        ],
        "color": "#7f8c8d",
    },

    "Rectangle Bottom": {
        "type": "continuation", "direction": "bullish",
        "category": "Rectangles",
        "description": "Horizontal trading range bounded by parallel support and resistance lines, after a downtrend. Bullish when breakout is upward.",
        "identification": [
            "Two distinct horizontal lines: support (bottom) and resistance (top)",
            "Price oscillates between the two lines at least twice",
            "Lines are roughly parallel",
            "Occurs after a prior downtrend",
            "Upward breakout: close above resistance line",
        ],
        "stats": {
            "bull_market": {
                "avg_rise": "36%",
                "breakeven_failure_rate": "11%",
                "throwback_rate": "56%",
                "avg_throwback_days": "10 days",
                "performance_rank": "Good",
                "samples": 614,
            },
            "bear_market": {
                "avg_rise": "27%",
                "breakeven_failure_rate": "17%",
                "throwback_rate": "48%",
                "avg_throwback_days": "10 days",
                "performance_rank": "Fair",
                "samples": 247,
            }
        },
        "measure_rule": "Rectangle height (top minus bottom) added to breakout price.",
        "target_reliability": "66%",
        "trading_plan": {
            "entry": "Close above resistance line (top of rectangle).",
            "stop": "Below support line (bottom of rectangle).",
            "target_1": "Resistance price + rectangle height.",
            "target_2": "Prior swing high above rectangle.",
            "exit_rule": "Throwback to resistance: hold if resistance holds as support.",
            "avoid": "Wide rectangles (long duration) can trap traders — prefer narrower ranges.",
        },
        "best_performance": [
            "Bull markets outperform substantially",
            "Short rectangles (narrow height) perform better",
            "Breakout on above-average volume gives better follow-through",
        ],
        "color": "#27ae60",
    },

    "Rectangle Top": {
        "type": "continuation", "direction": "bearish",
        "category": "Rectangles",
        "description": "Horizontal trading range after an uptrend. Bearish when breakout is downward.",
        "identification": [
            "Two horizontal lines: resistance (top) and support (bottom)",
            "Price oscillates between lines at least twice each",
            "Occurs after a prior uptrend",
            "Downward breakout: close below support line",
        ],
        "stats": {
            "bull_market": {
                "avg_decline": "14%",
                "breakeven_failure_rate": "18%",
                "pullback_rate": "51%",
                "avg_pullback_days": "10 days",
                "performance_rank": "Fair",
                "samples": 492,
            },
            "bear_market": {
                "avg_decline": "20%",
                "breakeven_failure_rate": "12%",
                "pullback_rate": "43%",
                "avg_pullback_days": "10 days",
                "performance_rank": "Good",
                "samples": 197,
            }
        },
        "measure_rule": "Rectangle height subtracted from breakout (support) price.",
        "target_reliability": "58% bear markets",
        "trading_plan": {
            "entry": "Close below support line.",
            "stop": "Above resistance line (rectangle top).",
            "target_1": "Support price minus rectangle height.",
            "target_2": "Prior support below rectangle.",
            "exit_rule": "Pullback to support level: hold if support acts as resistance.",
            "avoid": "Higher failure rate in bull markets (18%) — prefer bear market context.",
        },
        "best_performance": [
            "Bear market context significantly better",
            "Short patterns (narrow height) perform better",
        ],
        "color": "#e74c3c",
    },

    "Flag (Bull)": {
        "type": "continuation", "direction": "bullish",
        "category": "Flags and Pennants",
        "description": "Small rectangular consolidation pattern sloping slightly against the prevailing uptrend, resembling a flag on a pole. Short-term continuation.",
        "identification": [
            "Prior strong uptrend (the 'flagpole')",
            "Small rectangular consolidation, typically sloping slightly downward",
            "Lower volume during the flag formation than on the flagpole",
            "Short duration: typically 1–4 weeks",
            "Breakout: close above upper trendline of the flag",
        ],
        "stats": {
            "bull_market": {
                "avg_rise": "23%",
                "breakeven_failure_rate": "4%",
                "throwback_rate": "42%",
                "avg_throwback_days": "10 days",
                "performance_rank": "Good",
                "samples": 1014,
            },
            "bear_market": {
                "avg_rise": "17%",
                "breakeven_failure_rate": "9%",
                "throwback_rate": "37%",
                "avg_throwback_days": "9 days",
                "performance_rank": "Fair",
                "samples": 395,
            }
        },
        "measure_rule": "Flagpole height (rise from start of pole to top of pole) added to the flag low or breakout price. Note: flag is NOT a half-staff pattern per Bulkowski.",
        "target_reliability": "64% (bull market)",
        "trading_plan": {
            "entry": "Close above upper trendline of flag.",
            "stop": "Below the lowest low of the flag.",
            "target_1": "Flagpole height added to flag low.",
            "target_2": "Prior resistance above.",
            "exit_rule": "Low throwback rate = clean holds. Trail stop below each higher low.",
            "avoid": "Flags in bear markets perform worse. Avoid flags with large range bars (wide consolidation is not a tight flag).",
        },
        "best_performance": [
            "Very low failure rate (4% in bull markets)",
            "Low throwback rate = clean continuation",
            "Flagpole length: longer is better",
            "Tight, narrow flags outperform wide ones",
        ],
        "color": "#2ecc71",
    },

    "High and Tight Flag": {
        "type": "continuation", "direction": "bullish",
        "category": "Flags and Pennants",
        "description": "Exceptional pattern: stock doubles in 2 months or less, then forms a tight consolidation (10–25% retracement). One of Bulkowski's highest-rated patterns.",
        "identification": [
            "Stock rises 90%+ (ideally doubles) in 2 months or less",
            "Flag: small consolidation of 10–25% retracement",
            "Flag lasts 1–8 weeks",
            "Volume declines during flag, spikes on breakout",
            "Breakout: close above flag high",
        ],
        "stats": {
            "bull_market": {
                "avg_rise": "69%",
                "breakeven_failure_rate": "0%",
                "throwback_rate": "54%",
                "avg_throwback_days": "11 days",
                "performance_rank": "BEST",
                "samples": 307,
            },
            "bear_market": {
                "avg_rise": "42%",
                "breakeven_failure_rate": "0%",
                "throwback_rate": "43%",
                "avg_throwback_days": "10 days",
                "performance_rank": "Excellent",
                "samples": 54,
            }
        },
        "measure_rule": "Half the flagpole (start of pole to flag top) added to flag low. Target hit 90% of time.",
        "target_reliability": "90% (conservative half-pole measure)",
        "trading_plan": {
            "entry": "Close above flag high.",
            "stop": "Below flag low.",
            "target_1": "Conservative: half flagpole height + flag low.",
            "target_2": "Full flagpole height + flag low.",
            "exit_rule": "HOLD aggressively — this is Bulkowski's #1 rated pattern (0% failure rate). Accept throwbacks and hold.",
            "avoid": "Flag that retraces more than 50% of the flagpole. Pattern requires the stock to have truly doubled first.",
        },
        "best_performance": [
            "BEST PERFORMER in Bulkowski's entire database",
            "0% failure rate — never failed to rise at least 5% in samples",
            "Average 69% gain in bull markets",
            "This is the pattern to search hardest for",
        ],
        "color": "#f1c40f",
    },

    "Pennant (Bull)": {
        "type": "continuation", "direction": "bullish",
        "category": "Flags and Pennants",
        "description": "Small symmetrical triangle (converging lines) after a strong uptrend. Short consolidation before continuation.",
        "identification": [
            "Prior strong uptrend (flagpole)",
            "Small symmetrical triangle: converging upper and lower trendlines",
            "Volume decreases during pennant",
            "Duration: 1–4 weeks typically",
            "Breakout: close above upper trendline",
        ],
        "stats": {
            "bull_market": {
                "avg_rise": "19%",
                "breakeven_failure_rate": "5%",
                "throwback_rate": "37%",
                "avg_throwback_days": "10 days",
                "performance_rank": "Good",
                "samples": 522,
            },
            "bear_market": {
                "avg_rise": "15%",
                "breakeven_failure_rate": "10%",
                "throwback_rate": "34%",
                "avg_throwback_days": "9 days",
                "performance_rank": "Fair",
                "samples": 204,
            }
        },
        "measure_rule": "Flagpole height added to pennant low or breakout price.",
        "target_reliability": "56%",
        "trading_plan": {
            "entry": "Close above upper converging trendline.",
            "stop": "Below pennant low.",
            "target_1": "Flagpole height from pennant breakout.",
            "target_2": "Prior resistance above.",
            "exit_rule": "Low throwback rate = clean hold. Trail stop.",
            "avoid": "Pennant wider than flagpole (body bigger than pole = not a pennant).",
        },
        "best_performance": [
            "Low failure rate and low throwback rate = clean, manageable",
            "Bull market substantially outperforms",
        ],
        "color": "#3498db",
    },

    "Falling Wedge": {
        "type": "reversal", "direction": "bullish",
        "category": "Wedges",
        "description": "Two downward-sloping converging trendlines. Can be reversal or continuation. Breakout is usually upward.",
        "identification": [
            "Both trendlines slope downward with the upper declining faster than lower (converging)",
            "At least 2 touches on each trendline",
            "Volume typically decreases during formation",
            "Breakout: close above upper trendline (upward)",
        ],
        "stats": {
            "bull_market": {
                "avg_rise": "38%",
                "breakeven_failure_rate": "5%",
                "throwback_rate": "53%",
                "avg_throwback_days": "11 days",
                "upward_breakout_pct": "68%",
                "performance_rank": "Good",
                "samples": 706,
            },
            "bear_market": {
                "avg_rise": "25%",
                "breakeven_failure_rate": "10%",
                "throwback_rate": "45%",
                "avg_throwback_days": "10 days",
                "upward_breakout_pct": "65%",
                "performance_rank": "Fair",
                "samples": 280,
            }
        },
        "measure_rule": "Height at the widest point (left side) added to breakout price.",
        "target_reliability": "62%",
        "trading_plan": {
            "entry": "Close above upper trendline.",
            "stop": "Below wedge low.",
            "target_1": "Wedge height added to breakout.",
            "target_2": "Start of downtrend that led to the wedge.",
            "exit_rule": "Throwback to upper trendline: hold if trendline acts as support.",
            "avoid": "Downward breakout from a falling wedge underperforms — avoid the short side.",
        },
        "best_performance": [
            "Upward breakout occurs 65–68% of the time",
            "Tall patterns outperform short ones",
            "Bull market significantly better",
        ],
        "color": "#16a085",
    },

    "Rising Wedge": {
        "type": "reversal", "direction": "bearish",
        "category": "Wedges",
        "description": "Two upward-sloping converging trendlines. Bearish — lower trendline rises faster than upper, indicating buying exhaustion.",
        "identification": [
            "Both trendlines slope upward, converging",
            "Lower trendline has steeper angle than upper",
            "Volume decreases during formation",
            "At least 2 touches on each trendline",
            "Breakout: downward through lower trendline",
        ],
        "stats": {
            "bull_market": {
                "avg_decline": "14%",
                "breakeven_failure_rate": "24%",
                "pullback_rate": "68%",
                "avg_pullback_days": "11 days",
                "downward_breakout_pct": "69%",
                "performance_rank": "Fair",
                "samples": 618,
            },
            "bear_market": {
                "avg_decline": "22%",
                "breakeven_failure_rate": "10%",
                "pullback_rate": "57%",
                "avg_pullback_days": "10 days",
                "downward_breakout_pct": "74%",
                "performance_rank": "Good",
                "samples": 253,
            }
        },
        "measure_rule": "Wedge height subtracted from breakout price.",
        "target_reliability": "55%",
        "trading_plan": {
            "entry": "Close below lower trendline.",
            "stop": "Above wedge high.",
            "target_1": "Wedge height subtracted from breakout.",
            "target_2": "Start of rally leading to wedge.",
            "exit_rule": "Very high pullback rate (68% in bull) — be prepared. Hold if lower trendline holds as resistance.",
            "avoid": "High failure rate in bull markets (24%) — best traded in bear market context.",
        },
        "best_performance": [
            "Bear market context is much more reliable",
            "Downward breakout occurs 69–74% of the time",
            "Caution: highest failure rate in bull markets among common patterns",
        ],
        "color": "#d35400",
    },

    "Measured Move Up": {
        "type": "continuation", "direction": "bullish",
        "category": "Measured Moves",
        "description": "Two equal upward legs separated by a corrective phase. Leg 1 = Leg 2 in price distance. Useful for target projection.",
        "identification": [
            "Strong first leg up",
            "Correction phase: 30–60% retracement of leg 1",
            "Second leg up begins and matches the distance of leg 1",
            "Volume typically higher in leg 1 than correction, increases again in leg 2",
        ],
        "stats": {
            "bull_market": {
                "avg_rise": "26% (leg 2 after correction)",
                "breakeven_failure_rate": "7%",
                "throwback_rate": "38%",
                "performance_rank": "Good",
                "samples": 593,
            },
            "bear_market": {
                "avg_rise": "20%",
                "breakeven_failure_rate": "14%",
                "throwback_rate": "31%",
                "performance_rank": "Fair",
                "samples": 212,
            }
        },
        "measure_rule": "Measure leg 1 distance. Project same distance from the end of the correction.",
        "target_reliability": "75% for achieving the equal-leg target",
        "trading_plan": {
            "entry": "Enter long at end of correction phase (Higher Low formed, prior downtrend broken).",
            "stop": "Below the correction low.",
            "target_1": "Leg 1 distance + start of leg 2 = primary target.",
            "target_2": "1.5x Leg 1 if very strong momentum.",
            "exit_rule": "Exit at the measured target — leg 2 rarely continues beyond 100% of leg 1.",
            "avoid": "If correction exceeds 60% of leg 1 = move may not resume. If leg 1 is very small = measurement error risk.",
        },
        "best_performance": [
            "75% accuracy for achieving the measured target",
            "Low throwback rate = clean momentum holds",
            "Best used as a TARGET TOOL for all other setups",
        ],
        "color": "#2ecc71",
    },

    "Measured Move Down": {
        "type": "continuation", "direction": "bearish",
        "category": "Measured Moves",
        "description": "Two equal downward legs with a corrective bounce between them. Leg 1 = Leg 2 in distance. Projection tool.",
        "identification": [
            "Strong first leg down",
            "Corrective bounce: 30–60% retracement of leg 1",
            "Second leg down begins and targets equal distance to leg 1",
        ],
        "stats": {
            "bull_market": {
                "avg_decline": "19%",
                "breakeven_failure_rate": "10%",
                "pullback_rate": "29%",
                "performance_rank": "Fair",
                "samples": 398,
            },
            "bear_market": {
                "avg_decline": "27%",
                "breakeven_failure_rate": "6%",
                "pullback_rate": "24%",
                "performance_rank": "Good",
                "samples": 165,
            }
        },
        "measure_rule": "Leg 1 distance subtracted from start of leg 2.",
        "target_reliability": "72%",
        "trading_plan": {
            "entry": "Short at end of corrective bounce (Lower High formed, bounce structure breaking).",
            "stop": "Above the bounce high (correction high).",
            "target_1": "Leg 1 distance subtracted from end of correction.",
            "target_2": "Major support below.",
            "exit_rule": "Very low pullback rate = hold comfortably. Exit at measured target.",
            "avoid": "If bounce exceeds 60% of leg 1.",
        },
        "best_performance": [
            "Lowest pullback rate among major patterns — very clean short holds",
            "Bear market gives excellent 27% average decline",
            "Use primarily as a target projection tool",
        ],
        "color": "#e74c3c",
    },

    "Broadening Bottom": {
        "type": "reversal", "direction": "bullish",
        "category": "Broadening Formations",
        "description": "Expanding price action with lower lows and higher highs. Unusual pattern — both support and resistance diverge. Signals high volatility before reversal.",
        "identification": [
            "Price swings expand: each swing is larger than the previous",
            "Lower trendline: descending (lower lows)",
            "Upper trendline: ascending (higher highs)",
            "At least 3 touches on each trendline",
            "Breakout: close above upper trendline",
        ],
        "stats": {
            "bull_market": {
                "avg_rise": "26%",
                "breakeven_failure_rate": "20%",
                "throwback_rate": "53%",
                "performance_rank": "Fair",
                "samples": 235,
            },
            "bear_market": {
                "avg_rise": "21%",
                "breakeven_failure_rate": "26%",
                "throwback_rate": "44%",
                "performance_rank": "Poor",
                "samples": 95,
            }
        },
        "measure_rule": "Height at widest point added to breakout price.",
        "target_reliability": "55%",
        "trading_plan": {
            "entry": "Close above upper trendline (ascending resistance).",
            "stop": "Below the lowest low in the broadening pattern.",
            "target_1": "Widest height + breakout price.",
            "target_2": "Prior resistance above.",
            "exit_rule": "Higher failure rate — use tighter stops than normal.",
            "avoid": "One of the higher failure rate patterns. Only trade if pattern shape is very clear and breakout volume is high.",
        },
        "best_performance": [
            "Relatively high failure rates — approach with caution",
            "Wait for confirmed close above upper trendline",
            "Bull markets much better than bear markets",
        ],
        "color": "#95a5a6",
    },

    "Diamond Bottom": {
        "type": "reversal", "direction": "bullish",
        "category": "Diamond Patterns",
        "description": "Broadening formation followed by a narrowing formation — creates a diamond shape. Bullish reversal from a bottom.",
        "identification": [
            "First half: expanding range (broadening pattern)",
            "Second half: contracting range (symmetrical triangle shape)",
            "Overall shape looks like a diamond or rhombus",
            "Breakout: upward from the narrowing portion",
        ],
        "stats": {
            "bull_market": {
                "avg_rise": "36%",
                "breakeven_failure_rate": "6%",
                "throwback_rate": "53%",
                "avg_throwback_days": "13 days",
                "performance_rank": "Good",
                "samples": 115,
            },
            "bear_market": {
                "avg_rise": "22%",
                "breakeven_failure_rate": "16%",
                "throwback_rate": "40%",
                "avg_throwback_days": "11 days",
                "performance_rank": "Fair",
                "samples": 44,
            }
        },
        "measure_rule": "Diamond height (widest point) added to upward breakout price.",
        "target_reliability": "63%",
        "trading_plan": {
            "entry": "Close above upper trendline of narrowing portion.",
            "stop": "Below diamond low.",
            "target_1": "Diamond height + breakout price.",
            "target_2": "Prior resistance above.",
            "exit_rule": "Hold through throwback if upper trendline holds as support.",
            "avoid": "Pattern with only 2 touches per trendline — less reliable.",
        },
        "best_performance": [
            "Low failure rate (6%) in bull markets",
            "Good average rise",
            "Rare pattern — when you see it, it's worth trading carefully",
        ],
        "color": "#9b59b6",
    },

    "Diamond Top": {
        "type": "reversal", "direction": "bearish",
        "category": "Diamond Patterns",
        "description": "Diamond pattern at a top — broadening then narrowing, bearish breakdown.",
        "identification": [
            "Expanding range in first half (broadening)",
            "Contracting range in second half (converging)",
            "Diamond shape at a price peak",
            "Breakout: downward from narrowing portion",
        ],
        "stats": {
            "bull_market": {
                "avg_decline": "20%",
                "breakeven_failure_rate": "10%",
                "pullback_rate": "57%",
                "performance_rank": "Good",
                "samples": 143,
            },
            "bear_market": {
                "avg_decline": "25%",
                "breakeven_failure_rate": "7%",
                "pullback_rate": "48%",
                "performance_rank": "Good",
                "samples": 60,
            }
        },
        "measure_rule": "Diamond height subtracted from downward breakout price.",
        "target_reliability": "58%",
        "trading_plan": {
            "entry": "Close below lower trendline of narrowing portion.",
            "stop": "Above diamond high.",
            "target_1": "Diamond height subtracted from breakout.",
            "target_2": "Prior support below.",
            "exit_rule": "High pullback rate — hold through pullback if lower trendline acts as resistance.",
            "avoid": "Low sample count — confirmation is important.",
        },
        "best_performance": [
            "Bear market gives better performance",
            "Relatively low failure rate",
        ],
        "color": "#e74c3c",
    },

    "Horn Bottom": {
        "type": "reversal", "direction": "bullish",
        "category": "Horn Patterns",
        "description": "Two price spikes (V-shapes) separated by 1–3 weeks, at approximately the same low price. Signals selling exhaustion.",
        "identification": [
            "Two sharp downward spikes (horns) at approximately the same price",
            "Spikes separated by 1–3 weeks",
            "Each horn is a clear spike low (sharp, pointed)",
            "Second horn at same level or slightly higher than first",
            "Breakout: close above the peak between the two horns",
        ],
        "stats": {
            "bull_market": {
                "avg_rise": "35%",
                "breakeven_failure_rate": "4%",
                "throwback_rate": "50%",
                "performance_rank": "Good",
                "samples": 346,
            },
            "bear_market": {
                "avg_rise": "24%",
                "breakeven_failure_rate": "11%",
                "throwback_rate": "42%",
                "performance_rank": "Fair",
                "samples": 125,
            }
        },
        "measure_rule": "Height from horn low to peak between horns, added to peak price.",
        "target_reliability": "65%",
        "trading_plan": {
            "entry": "Close above the peak between the two horns.",
            "stop": "Below the lower of the two horn lows.",
            "target_1": "Pattern height + peak price.",
            "target_2": "Prior resistance above.",
            "exit_rule": "Low failure rate — hold through throwback.",
            "avoid": "Horns separated by more than 3 weeks — less reliable timing.",
        },
        "best_performance": [
            "Low failure rate (4%) in bull markets",
            "Good average rise",
        ],
        "color": "#1abc9c",
    },

    "Pipe Bottom": {
        "type": "reversal", "direction": "bullish",
        "category": "Pipe Patterns",
        "description": "Two adjacent weeks (on weekly chart) with similar long lower shadows (wicks) forming a double bottom spike. Reliable weekly chart pattern.",
        "identification": [
            "On weekly chart: two adjacent bars with nearly identical lows",
            "Both bars have long lower shadows (wicks)",
            "Pattern spans exactly 2 weeks",
            "Breakout: week-close above the high of the second pipe bar",
        ],
        "stats": {
            "bull_market": {
                "avg_rise": "45%",
                "breakeven_failure_rate": "5%",
                "throwback_rate": "41%",
                "performance_rank": "Excellent",
                "samples": 427,
            },
            "bear_market": {
                "avg_rise": "29%",
                "breakeven_failure_rate": "9%",
                "throwback_rate": "35%",
                "performance_rank": "Good",
                "samples": 168,
            }
        },
        "measure_rule": "Height of the pipe (from pipe low to breakout) added to breakout price.",
        "target_reliability": "68%",
        "trading_plan": {
            "entry": "Weekly close above the high of the second pipe bar.",
            "stop": "Below the pipe low.",
            "target_1": "Pipe height added to breakout price.",
            "target_2": "Prior resistance on weekly chart.",
            "exit_rule": "Low throwback rate = clean weekly holds.",
            "avoid": "Pipes that form mid-trend (not at a bottom). Works best at trend exhaustion points.",
        },
        "best_performance": [
            "One of the best performers — 45% average rise in bull markets",
            "Low failure rate and low throwback rate",
            "Works on weekly charts primarily — do not apply to daily",
        ],
        "color": "#f39c12",
    },

    "Island Reversal (Bottom)": {
        "type": "reversal", "direction": "bullish",
        "category": "Island Patterns",
        "description": "A price island formed by two gaps — gap down to island, then gap up away. Signals dramatic reversal.",
        "identification": [
            "Gap down below prior price action (creates island on the low side)",
            "Price consolidates for 1 or a few days at the island level",
            "Gap up away from the island level (second gap)",
            "Both gaps should be in the same price area",
        ],
        "stats": {
            "bull_market": {
                "avg_rise": "37%",
                "breakeven_failure_rate": "1%",
                "throwback_rate": "35%",
                "performance_rank": "Excellent",
                "samples": 212,
            },
            "bear_market": {
                "avg_rise": "24%",
                "breakeven_failure_rate": "5%",
                "throwback_rate": "28%",
                "performance_rank": "Good",
                "samples": 84,
            }
        },
        "measure_rule": "Height from island low to the gap's upper boundary, added to breakout price.",
        "target_reliability": "67%",
        "trading_plan": {
            "entry": "Enter on the gap-up day (the second gap) — gap itself is the signal.",
            "stop": "Below the island low.",
            "target_1": "Prior resistance before the island formation.",
            "target_2": "Measured move based on island height.",
            "exit_rule": "Lowest throwback rate — hold aggressively.",
            "avoid": "Small island on light volume — best when both gaps are accompanied by high volume.",
        },
        "best_performance": [
            "Extremely low failure rate (1%) in bull markets",
            "Lowest throwback rate — cleanest hold of all patterns",
            "Very reliable but rare — when you see it, prioritize it",
        ],
        "color": "#3498db",
    },

}

# ─────────────────────────────────────────────────────────────────────────────
#  PATTERN DETECTION ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def find_swing_highs_lows(df, order=5):
    """Find local highs and lows using scipy argrelextrema."""
    highs_idx = argrelextrema(df['High'].values, np.greater_equal, order=order)[0]
    lows_idx  = argrelextrema(df['Low'].values,  np.less_equal,    order=order)[0]
    return highs_idx, lows_idx


def pct_diff(a, b):
    """Percentage difference between two values."""
    if b == 0: return float('inf')
    return abs(a - b) / b * 100


def get_completion_status(pat, df):
    """
    Assess how complete / confirmed a pattern is.
    Returns a dict with status label, percentage, and description.
    """
    closes  = df['Close'].values
    highs   = df['High'].values
    lows    = df['Low'].values
    current = closes[-1]
    name    = pat['name']

    neckline     = pat.get('neckline')
    pattern_low  = pat.get('pattern_low')
    pattern_high = pat.get('pattern_high')

    # ── BULLISH PATTERNS ─────────────────────────────────────────────────────
    if pat['direction'] in ('BULLISH', 'BULLISH (70% breakout upward)',
                            'BULLISH (prior uptrend)'):
        if neckline is None:
            return {'status': '🔄 FORMING', 'pct': 50,
                    'color': '#f39c12',
                    'desc': 'Pattern identified. Waiting for key level.'}

        dist_to_neck   = neckline - current
        pattern_height = neckline - pattern_low if pattern_low else 1

        if current > neckline * 1.002:          # closed above neckline
            return {'status': '✅ CONFIRMED BREAKOUT', 'pct': 100,
                    'color': '#2ecc71',
                    'desc': f'Price ({current:.2f}) closed ABOVE neckline '
                            f'({neckline:.2f}). Pattern is ACTIVE. '
                            f'Enter long now or on any pullback to neckline.'}
        elif current > neckline * 0.995:        # within 0.5 % of neckline
            return {'status': '⚡ BREAKOUT IMMINENT', 'pct': 90,
                    'color': '#f1c40f',
                    'desc': f'Price ({current:.2f}) is pressing neckline '
                            f'({neckline:.2f}). Watch for a closing candle '
                            f'above the neckline to confirm entry.'}
        else:
            pct_done = max(10, min(85,
                           100 - (dist_to_neck / pattern_height * 100)))
            return {'status': '🔄 FORMING', 'pct': round(pct_done),
                    'color': '#3498db',
                    'desc': f'Price ({current:.2f}) is {dist_to_neck:.2f} pts '
                            f'below neckline ({neckline:.2f}). '
                            f'Pattern is still building. Do NOT enter yet — '
                            f'wait for neckline breakout close.'}

    # ── BEARISH PATTERNS ─────────────────────────────────────────────────────
    elif 'BEARISH' in pat['direction']:
        if neckline is None:
            return {'status': '🔄 FORMING', 'pct': 50,
                    'color': '#f39c12',
                    'desc': 'Pattern identified. Waiting for key level.'}

        dist_to_neck   = current - neckline
        pattern_height = (pattern_high - neckline) if pattern_high else 1

        if current < neckline * 0.998:          # closed below neckline
            return {'status': '✅ CONFIRMED BREAKDOWN', 'pct': 100,
                    'color': '#e74c3c',
                    'desc': f'Price ({current:.2f}) closed BELOW neckline '
                            f'({neckline:.2f}). Pattern is ACTIVE. '
                            f'Enter short now or on any pullback to neckline.'}
        elif current < neckline * 1.005:        # within 0.5 %
            return {'status': '⚡ BREAKDOWN IMMINENT', 'pct': 90,
                    'color': '#f1c40f',
                    'desc': f'Price ({current:.2f}) is pressing support '
                            f'({neckline:.2f}). Watch for a closing candle '
                            f'below the neckline to confirm short entry.'}
        else:
            pct_done = max(10, min(85,
                           100 - (dist_to_neck / pattern_height * 100)))
            return {'status': '🔄 FORMING', 'pct': round(pct_done),
                    'color': '#3498db',
                    'desc': f'Price ({current:.2f}) is {dist_to_neck:.2f} pts '
                            f'above neckline ({neckline:.2f}). '
                            f'Pattern forming. Wait for breakdown close.'}

    # ── NEUTRAL ───────────────────────────────────────────────────────────────
    return {'status': '🔄 FORMING', 'pct': 60,
            'color': '#7f8c8d',
            'desc': 'Watch for breakout in either direction.'}


def calc_rr(entry, stop, target):
    """
    Calculate risk, reward, R:R ratio and a trade quality grade.
    Returns dict with all fields.
    """
    risk   = abs(entry - stop)
    reward = abs(target - entry)
    if risk == 0:
        return None
    rr = reward / risk

    if rr >= 3.0:
        grade = 'A+  EXCELLENT'
        grade_color = '#2ecc71'
        advice = 'Strong setup. Full position size appropriate.'
    elif rr >= 2.0:
        grade = 'A   GOOD'
        grade_color = '#27ae60'
        advice = 'Good setup. Standard position size.'
    elif rr >= 1.5:
        grade = 'B   ACCEPTABLE'
        grade_color = '#f1c40f'
        advice = 'Acceptable. Consider half position size.'
    elif rr >= 1.0:
        grade = 'C   MINIMUM'
        grade_color = '#e67e22'
        advice = 'Bare minimum. Only trade if pattern confidence > 80%.'
    else:
        grade = 'D   SKIP'
        grade_color = '#e74c3c'
        advice = 'Risk outweighs reward. DO NOT trade this setup.'

    return {
        'risk':        round(risk,   2),
        'reward':      round(reward, 2),
        'rr':          round(rr,     2),
        'grade':       grade,
        'grade_color': grade_color,
        'advice':      advice,
    }



# ─────────────────────────────────────────────────────────────────────────────
#  KAKUSHADZE QUANTITATIVE SIGNAL ENGINE
#  Source: 151 Trading Strategies — Kakushadze & Serur (2018)
#  All signals computed purely from OHLC data — no external data needed
# ─────────────────────────────────────────────────────────────────────────────

def _sma(series, n):
    """Simple Moving Average."""
    return series.rolling(window=n, min_periods=1).mean()

def _ema(series, n):
    """Exponential Moving Average."""
    return series.ewm(span=n, adjust=False).mean()

def _stddev(series, n):
    """Rolling standard deviation."""
    return series.rolling(window=n, min_periods=2).std()

def compute_quant_signals(df):
    """
    Compute all 6 Kakushadze quantitative signals from OHLC data.
    Returns a list of signal dicts with name, value, signal, strength, description.

    Strategies implemented (all from Ch.3 & Ch.10 of 151 Trading Strategies):
      1. Single Moving Average (Ch.3.11)       — trend direction
      2. Dual MA Crossover (Ch.3.12)           — trend confirmation
      3. Three MA Alignment (Ch.3.13)          — trend strength
      4. Donchian Channel / Ch.3.15            — breakout signal
      5. Z-Score Mean Reversion (Ch.3.9)       — overbought/oversold
      6. Price Momentum 12-1 (Ch.3.1)          — momentum filter
      7. Historical Volatility Rank (Ch.3.4)   — low-vol anomaly
      8. Contrarian Futures (Ch.10.3)          — short-term reversion
    """
    signals = []
    close  = df['Close']
    high   = df['High']
    low    = df['Low']
    n      = len(df)
    current_price = close.iloc[-1]

    # ── 1. SINGLE MOVING AVERAGE — Ch.3.11 ───────────────────────────────────
    # Signal = +1 (long) if Price > SMA(200); -1 (short) if Price < SMA(200)
    period_200 = min(200, n - 1)
    period_50  = min(50,  n - 1)
    sma200 = _sma(close, period_200).iloc[-1]
    sma50  = _sma(close, period_50).iloc[-1]

    above_200 = current_price > sma200
    pct_from_200 = (current_price - sma200) / sma200 * 100

    signals.append({
        'name'   : 'Single MA Filter (200-day)',
        'source' : 'Kakushadze Ch.3.11',
        'signal' : 'BULLISH' if above_200 else 'BEARISH',
        'icon'   : '▲' if above_200 else '▼',
        'color'  : '#2ecc71' if above_200 else '#e74c3c',
        'value'  : f"SMA(200) = {sma200:,.2f}  |  Price {'+' if pct_from_200>=0 else ''}{pct_from_200:.1f}% from MA",
        'strength': min(100, abs(pct_from_200) * 5),
        'desc'   : (
            f"Price ({current_price:,.2f}) is {'ABOVE' if above_200 else 'BELOW'} the 200-day SMA ({sma200:,.2f}).\n"
            f"Kakushadze: Signal = +1 when Price > SMA → trade longs only.\n"
            f"Signal = -1 when Price < SMA → trade shorts only.\n"
            f"This is the primary trend direction filter."
        ),
        'trade_rule': (
            "→ Only take LONG patterns when price is ABOVE the 200-day SMA.\n"
            "→ Only take SHORT patterns when price is BELOW the 200-day SMA."
        ),
    })

    # ── 2. DUAL MA CROSSOVER — Ch.3.12 ───────────────────────────────────────
    # Signal = +1 if SMA(50) > SMA(200) (Golden Cross active)
    # Signal = -1 if SMA(50) < SMA(200) (Death Cross active)
    golden_cross = sma50 > sma200
    cross_gap_pct = (sma50 - sma200) / sma200 * 100

    # Check if a crossover happened recently (last 10 bars)
    if n >= 15:
        sma50_series  = _sma(close, min(50,  n-1))
        sma200_series = _sma(close, min(200, n-1))
        prev_golden = sma50_series.iloc[-10] > sma200_series.iloc[-10]
        fresh_cross = (golden_cross != prev_golden)
        cross_text  = " ← FRESH CROSSOVER!" if fresh_cross else ""
    else:
        cross_text = ""

    signals.append({
        'name'   : 'Dual MA Crossover (50/200)',
        'source' : 'Kakushadze Ch.3.12',
        'signal' : 'BULLISH' if golden_cross else 'BEARISH',
        'icon'   : '▲' if golden_cross else '▼',
        'color'  : '#2ecc71' if golden_cross else '#e74c3c',
        'value'  : f"SMA(50) = {sma50:,.2f}  |  SMA(200) = {sma200:,.2f}  |  Gap: {cross_gap_pct:+.2f}%{cross_text}",
        'strength': min(100, abs(cross_gap_pct) * 10),
        'desc'   : (
            f"{'Golden Cross (SMA50 > SMA200)' if golden_cross else 'Death Cross (SMA50 < SMA200)'} is ACTIVE.\n"
            f"SMA(50) = {sma50:,.2f}  |  SMA(200) = {sma200:,.2f}\n"
            f"Gap between MAs: {cross_gap_pct:+.2f}%{cross_text}\n"
            f"Kakushadze: Trade in the direction of the faster MA relative to the slower MA."
        ),
        'trade_rule': (
            "→ Golden Cross active: prefer LONG setups from Bulkowski patterns.\n"
            "→ Death Cross active: prefer SHORT setups from Bulkowski patterns.\n"
            "→ Fresh crossover: higher urgency — trend just changed."
        ),
    })

    # ── 3. THREE MA ALIGNMENT — Ch.3.13 ──────────────────────────────────────
    # Strongest signal: SMA(20) > SMA(50) > SMA(200) = strong uptrend
    period_20 = min(20, n - 1)
    sma20 = _sma(close, period_20).iloc[-1]

    all_aligned_bull = sma20 > sma50 > sma200
    all_aligned_bear = sma20 < sma50 < sma200
    mixed = not (all_aligned_bull or all_aligned_bear)

    if all_aligned_bull:
        align_signal = 'STRONG BULL'
        align_color  = '#27ae60'
        align_icon   = '▲▲'
    elif all_aligned_bear:
        align_signal = 'STRONG BEAR'
        align_color  = '#c0392b'
        align_icon   = '▼▼'
    else:
        align_signal = 'MIXED'
        align_color  = '#f39c12'
        align_icon   = '◆'

    signals.append({
        'name'   : 'Three MA Alignment (20/50/200)',
        'source' : 'Kakushadze Ch.3.13',
        'signal' : align_signal,
        'icon'   : align_icon,
        'color'  : align_color,
        'value'  : f"SMA(20)={sma20:,.2f}  SMA(50)={sma50:,.2f}  SMA(200)={sma200:,.2f}",
        'strength': 100 if (all_aligned_bull or all_aligned_bear) else 40,
        'desc'   : (
            f"Three MA Alignment: {align_signal}\n"
            f"SMA(20) = {sma20:,.2f}\n"
            f"SMA(50) = {sma50:,.2f}\n"
            f"SMA(200) = {sma200:,.2f}\n"
            f"Kakushadze: All three MAs aligned in same direction = highest trend confidence.\n"
            f"{'✅ All three MAs aligned!' if not mixed else '⚠ MAs are mixed — lower trend confidence.'}"
        ),
        'trade_rule': (
            "→ All three aligned BULL: only take long patterns. Full position size.\n"
            "→ All three aligned BEAR: only take short patterns. Full position size.\n"
            "→ Mixed alignment: reduce position size by 50%. Trend is unclear."
        ),
    })

    # ── 4. DONCHIAN CHANNEL — Ch.3.14 & Ch.3.15 ──────────────────────────────
    # Upper = max(High, 20 days), Lower = min(Low, 20 days)
    # Buy when price breaks above upper, sell when breaks below lower
    dc_period = min(20, n - 1)
    dc_high   = high.rolling(dc_period).max().iloc[-1]
    dc_low    = low.rolling(dc_period).min().iloc[-1]
    dc_mid    = (dc_high + dc_low) / 2
    dc_range  = dc_high - dc_low
    dc_pos    = (current_price - dc_low) / dc_range * 100 if dc_range > 0 else 50

    if dc_pos >= 90:
        dc_signal = 'BREAKOUT HIGH'
        dc_color  = '#2ecc71'
        dc_icon   = '▲'
        dc_str    = 95
    elif dc_pos <= 10:
        dc_signal = 'BREAKOUT LOW'
        dc_color  = '#e74c3c'
        dc_icon   = '▼'
        dc_str    = 95
    elif dc_pos >= 60:
        dc_signal = 'UPPER HALF'
        dc_color  = '#3498db'
        dc_icon   = '◆'
        dc_str    = 60
    elif dc_pos <= 40:
        dc_signal = 'LOWER HALF'
        dc_color  = '#e67e22'
        dc_icon   = '◆'
        dc_str    = 60
    else:
        dc_signal = 'MIDRANGE'
        dc_color  = '#7f8c8d'
        dc_icon   = '◆'
        dc_str    = 30

    signals.append({
        'name'   : f'Donchian Channel (20-day)',
        'source' : 'Kakushadze Ch.3.14 / Ch.3.15',
        'signal' : dc_signal,
        'icon'   : dc_icon,
        'color'  : dc_color,
        'value'  : f"Upper={dc_high:,.2f}  Lower={dc_low:,.2f}  Position={dc_pos:.0f}th percentile",
        'strength': dc_str,
        'desc'   : (
            f"20-day Donchian Channel:\n"
            f"  Upper band (20d High): {dc_high:,.2f}\n"
            f"  Lower band (20d Low):  {dc_low:,.2f}\n"
            f"  Midpoint:              {dc_mid:,.2f}\n"
            f"  Current price position: {dc_pos:.0f}th percentile of range\n\n"
            f"Kakushadze (Ch.3.14): Buy on breakout above upper band.\n"
            f"Sell on breakout below lower band. (Turtle System equivalent)"
        ),
        'trade_rule': (
            "→ Price at/above upper band (≥90th %ile): Bullish breakout in progress.\n"
            "  Confirms bullish Bulkowski patterns.\n"
            "→ Price at/below lower band (≤10th %ile): Bearish breakout in progress.\n"
            "  Confirms bearish Bulkowski patterns.\n"
            "→ Price in midrange: no Donchian signal — neutral."
        ),
    })

    # ── 5. Z-SCORE MEAN REVERSION — Ch.3.9 ───────────────────────────────────
    # z = (Price - SMA(20)) / StdDev(20)
    # Buy when z < -2 (deeply oversold), Sell when z > +2 (deeply overbought)
    mr_period = min(20, n - 1)
    mr_mean   = _sma(close, mr_period).iloc[-1]
    mr_std    = _stddev(close, mr_period).iloc[-1]
    z_score   = (current_price - mr_mean) / mr_std if mr_std > 0 else 0

    if z_score <= -2.0:
        z_signal = 'DEEPLY OVERSOLD'
        z_color  = '#2ecc71'
        z_icon   = '▲'
        z_str    = 90
        z_note   = '→ STRONG buy signal for mean reversion long entry'
    elif z_score <= -1.0:
        z_signal = 'OVERSOLD'
        z_color  = '#27ae60'
        z_icon   = '▲'
        z_str    = 65
        z_note   = '→ Moderate buy signal. Confirms bullish patterns.'
    elif z_score >= 2.0:
        z_signal = 'DEEPLY OVERBOUGHT'
        z_color  = '#e74c3c'
        z_icon   = '▼'
        z_str    = 90
        z_note   = '→ STRONG sell signal. Wait for pullback before buying.'
    elif z_score >= 1.0:
        z_signal = 'OVERBOUGHT'
        z_color  = '#e67e22'
        z_icon   = '▼'
        z_str    = 65
        z_note   = '→ Moderate sell signal. Reduce size on longs.'
    else:
        z_signal = 'NEUTRAL'
        z_color  = '#7f8c8d'
        z_icon   = '◆'
        z_str    = 30
        z_note   = '→ Price near its mean. No extreme reversion signal.'

    signals.append({
        'name'   : 'Z-Score Mean Reversion',
        'source' : 'Kakushadze Ch.3.9',
        'signal' : z_signal,
        'icon'   : z_icon,
        'color'  : z_color,
        'value'  : f"Z-Score = {z_score:+.2f}  (Mean={mr_mean:,.2f}  StdDev={mr_std:,.2f})",
        'strength': z_str,
        'desc'   : (
            f"20-day Z-Score Mean Reversion:\n"
            f"  Z-Score = (Price - SMA20) / StdDev20\n"
            f"  Z-Score = ({current_price:,.2f} - {mr_mean:,.2f}) / {mr_std:,.2f} = {z_score:+.2f}\n\n"
            f"  Status: {z_signal}\n"
            f"  {z_note}\n\n"
            f"Kakushadze (Ch.3.9): z < -2 = oversold → buy mean reversion.\n"
            f"z > +2 = overbought → short or wait for pullback."
        ),
        'trade_rule': (
            "→ Z-Score ≤ -2.0: Deeply oversold. Strong confirmation for BULLISH patterns.\n"
            "   Enter aggressively — price is stretched far below mean.\n"
            "→ Z-Score ≥ +2.0: Deeply overbought. Do NOT enter new longs.\n"
            "   Wait for pullback. Short patterns are higher probability.\n"
            "→ Z-Score between -1 and +1: Neutral — no mean reversion signal."
        ),
    })

    # ── 6. PRICE MOMENTUM 12-1 — Ch.3.1 ──────────────────────────────────────
    # Cumulative return over last 12 months skipping most recent 1 month
    # R_cum = Price(11 months ago) / Price(12 months ago) - 1
    bars_12m = min(252, n - 1)
    bars_1m  = min(21,  n - 1)

    if n > bars_1m + 5:
        price_12m_ago = close.iloc[max(0, n - bars_12m)]
        price_1m_ago  = close.iloc[max(0, n - bars_1m)]
        mom_return    = (price_1m_ago - price_12m_ago) / price_12m_ago * 100
        recent_return = (current_price - price_1m_ago) / price_1m_ago * 100

        if mom_return >= 15:
            mom_signal = 'STRONG MOMENTUM'
            mom_color  = '#2ecc71'
            mom_icon   = '▲'
            mom_str    = 90
        elif mom_return >= 5:
            mom_signal = 'POSITIVE'
            mom_color  = '#27ae60'
            mom_icon   = '▲'
            mom_str    = 65
        elif mom_return <= -15:
            mom_signal = 'STRONG NEGATIVE'
            mom_color  = '#e74c3c'
            mom_icon   = '▼'
            mom_str    = 90
        elif mom_return <= -5:
            mom_signal = 'NEGATIVE'
            mom_color  = '#e67e22'
            mom_icon   = '▼'
            mom_str    = 65
        else:
            mom_signal = 'NEUTRAL'
            mom_color  = '#7f8c8d'
            mom_icon   = '◆'
            mom_str    = 30

        signals.append({
            'name'   : 'Price Momentum (12-1 Month)',
            'source' : 'Kakushadze Ch.3.1',
            'signal' : mom_signal,
            'icon'   : mom_icon,
            'color'  : mom_color,
            'value'  : f"12m Return (skip 1m) = {mom_return:+.1f}%  |  Recent 1m = {recent_return:+.1f}%",
            'strength': mom_str,
            'desc'   : (
                f"Price Momentum (12 months, skip 1 month):\n"
                f"  Price 12m ago: {price_12m_ago:,.2f}\n"
                f"  Price 1m ago:  {price_1m_ago:,.2f}\n"
                f"  Current price: {current_price:,.2f}\n\n"
                f"  12-month momentum return: {mom_return:+.1f}%\n"
                f"  Most recent 1-month:      {recent_return:+.1f}%\n\n"
                f"Kakushadze (Ch.3.1): Buy top-momentum stocks.\n"
                f"Skip most recent 1 month to avoid short-term reversal noise."
            ),
            'trade_rule': (
                "→ Strong positive momentum (>15%): Bullish bias. Prefer long setups.\n"
                "→ Strong negative momentum (<-15%): Bearish bias. Prefer short setups.\n"
                "→ Neutral zone (-5% to +5%): No momentum edge. Focus on pattern quality only.\n"
                "→ Most recent 1m drop while 12m is positive: potential buying opportunity."
            ),
        })
    else:
        signals.append({
            'name': 'Price Momentum (12-1 Month)',
            'source': 'Kakushadze Ch.3.1',
            'signal': 'INSUFFICIENT DATA',
            'icon': '?', 'color': '#7f8c8d',
            'value': f'Need at least 22 bars. Have {n}.',
            'strength': 0,
            'desc': 'Load more historical data (ideally 1+ year) for momentum calculation.',
            'trade_rule': 'Insufficient data.',
        })

    # ── 7. HISTORICAL VOLATILITY RANK — Ch.3.4 ───────────────────────────────
    # Low-Volatility Anomaly: low-vol stocks outperform high-vol stocks
    # Compute 20-day historical volatility (annualized)
    vol_period = min(20, n - 2)
    returns    = close.pct_change()
    hv_current = returns.rolling(vol_period).std().iloc[-1] * (252 ** 0.5) * 100

    # Compute rolling HV over past 252 bars to get percentile rank
    if n > 30:
        hv_series = returns.rolling(vol_period).std() * (252 ** 0.5) * 100
        hv_series = hv_series.dropna()
        hv_rank   = (hv_series < hv_current).mean() * 100  # percentile
    else:
        hv_rank = 50.0

    if hv_rank <= 25:
        vol_signal = 'LOW VOLATILITY'
        vol_color  = '#2ecc71'
        vol_icon   = '▲'
        vol_str    = 80
        vol_note   = 'Low-vol anomaly: historically outperforms. Good entry window.'
    elif hv_rank >= 75:
        vol_signal = 'HIGH VOLATILITY'
        vol_color  = '#e74c3c'
        vol_icon   = '▼'
        vol_str    = 30
        vol_note   = 'High volatility: reduce position size. Wider stops needed.'
    else:
        vol_signal = 'NORMAL VOLATILITY'
        vol_color  = '#3498db'
        vol_icon   = '◆'
        vol_str    = 55
        vol_note   = 'Volatility is in normal range. Standard position sizing.'

    signals.append({
        'name'   : 'Historical Volatility Rank',
        'source' : 'Kakushadze Ch.3.4',
        'signal' : vol_signal,
        'icon'   : vol_icon,
        'color'  : vol_color,
        'value'  : f"HV(20d annualized) = {hv_current:.1f}%  |  Rank = {hv_rank:.0f}th percentile",
        'strength': vol_str,
        'desc'   : (
            f"Historical Volatility (20-day, annualized):\n"
            f"  Current HV:      {hv_current:.1f}% annualized\n"
            f"  Volatility rank: {hv_rank:.0f}th percentile (vs past {min(n,252)} bars)\n\n"
            f"  {vol_note}\n\n"
            f"Kakushadze (Ch.3.4) Low-Volatility Anomaly:\n"
            f"Empirically, low-volatility stocks outperform high-volatility stocks\n"
            f"— counter to intuition that higher risk = higher reward."
        ),
        'trade_rule': (
            "→ Low volatility (≤25th %ile): Favor entry. Low-vol anomaly in effect.\n"
            "   Use standard position size.\n"
            "→ High volatility (≥75th %ile): Caution. Wider stops, smaller size.\n"
            "   Patterns may fail more frequently in high-vol environments.\n"
            "→ Normal volatility: Standard approach."
        ),
    })

    # ── 8. SHORT-TERM CONTRARIAN / MEAN REVERSION — Ch.10.3 ─────────────────
    # If price moved strongly one direction in last 5 days: fade it
    bars_5d = min(5, n - 2)
    ret_5d  = (current_price - close.iloc[-bars_5d - 1]) / close.iloc[-bars_5d - 1] * 100

    if ret_5d <= -5:
        ct_signal = 'OVERSOLD (5d)'
        ct_color  = '#2ecc71'
        ct_icon   = '▲'
        ct_str    = 75
        ct_note   = 'Short-term oversold. Contrarian buy signal (mean reversion).'
    elif ret_5d >= 5:
        ct_signal = 'OVERBOUGHT (5d)'
        ct_color  = '#e74c3c'
        ct_icon   = '▼'
        ct_str    = 75
        ct_note   = 'Short-term overbought. Contrarian sell signal (mean reversion).'
    elif ret_5d <= -2:
        ct_signal = 'MILD OVERSOLD'
        ct_color  = '#27ae60'
        ct_icon   = '▲'
        ct_str    = 50
        ct_note   = 'Mild 5-day pullback. Slight contrarian buy bias.'
    elif ret_5d >= 2:
        ct_signal = 'MILD OVERBOUGHT'
        ct_color  = '#e67e22'
        ct_icon   = '▼'
        ct_str    = 50
        ct_note   = 'Mild 5-day run-up. Slight contrarian sell bias.'
    else:
        ct_signal = 'NEUTRAL (5d)'
        ct_color  = '#7f8c8d'
        ct_icon   = '◆'
        ct_str    = 20
        ct_note   = 'No significant 5-day move. No contrarian signal.'

    signals.append({
        'name'   : 'Short-Term Contrarian (5-day)',
        'source' : 'Kakushadze Ch.10.3',
        'signal' : ct_signal,
        'icon'   : ct_icon,
        'color'  : ct_color,
        'value'  : f"5-day return = {ret_5d:+.2f}%",
        'strength': ct_str,
        'desc'   : (
            f"Short-Term Contrarian (Mean Reversion) Signal:\n"
            f"  5-day price return: {ret_5d:+.2f}%\n\n"
            f"  {ct_note}\n\n"
            f"Kakushadze (Ch.10.3): In futures and stocks, extreme short-term\n"
            f"moves tend to partially reverse within 1–5 days.\n"
            f"Fade strong 5-day moves, especially when confirmed by Z-score."
        ),
        'trade_rule': (
            "→ Deeply oversold (≤-5%): Short-term bounce likely.\n"
            "   Strong confirmation for bullish Bulkowski patterns.\n"
            "→ Deeply overbought (≥+5%): Short-term pullback likely.\n"
            "   Caution on bullish patterns — wait for the pullback.\n"
            "→ Best when this signal AGREES with the Z-Score signal."
        ),
    })

    # ── 9. PIVOT POINT SUPPORT & RESISTANCE — Ch.3.14 ────────────────────────
    # C=(H+L+C)/3, R=2C-L, S=2C-H using previous day's HLC
    # Signal: Long if P>C, exit at R. Short if P<C, exit at S.
    if n >= 2:
        prev  = df.iloc[-2]
        ph, pl, pc = prev['High'], prev['Low'], prev['Close']
        pivot_c = (ph + pl + pc) / 3.0
        pivot_r = 2 * pivot_c - pl   # resistance
        pivot_s = 2 * pivot_c - ph   # support
        pivot_r2 = pivot_c + (ph - pl)
        pivot_s2 = pivot_c - (ph - pl)

        above_pivot = current_price > pivot_c
        near_support    = current_price <= pivot_s * 1.002
        near_resistance = current_price >= pivot_r * 0.998

        if near_support:
            pv_signal = 'AT SUPPORT — BUY ZONE'
            pv_color  = '#2ecc71'; pv_icon = '▲'; pv_str = 85
        elif near_resistance:
            pv_signal = 'AT RESISTANCE — SELL ZONE'
            pv_color  = '#e74c3c'; pv_icon = '▼'; pv_str = 85
        elif above_pivot:
            pv_signal = 'ABOVE PIVOT — BULLISH'
            pv_color  = '#27ae60'; pv_icon = '▲'; pv_str = 60
        else:
            pv_signal = 'BELOW PIVOT — BEARISH'
            pv_color  = '#e67e22'; pv_icon = '▼'; pv_str = 60

        signals.append({
            'name'   : 'Pivot Point S&R',
            'source' : 'Kakushadze Ch.3.14',
            'signal' : pv_signal,
            'icon'   : pv_icon,
            'color'  : pv_color,
            'value'  : (f"Pivot={pivot_c:.2f}  R1={pivot_r:.2f}  R2={pivot_r2:.2f}  "
                        f"S1={pivot_s:.2f}  S2={pivot_s2:.2f}"),
            'strength': pv_str,
            'desc'   : (
                f"Classic Pivot Point (previous day HLC):\n"
                f"  Pivot (C): {pivot_c:.2f}\n"
                f"  Resistance R1: {pivot_r:.2f}  R2: {pivot_r2:.2f}\n"
                f"  Support    S1: {pivot_s:.2f}  S2: {pivot_s2:.2f}\n"
                f"  Current price: {current_price:.2f}\n\n"
                f"Kakushadze (Ch.3.14): Long if P > Pivot, exit at R1.\n"
                f"Short if P < Pivot, exit at S1.\n"
                f"R2/S2 are secondary targets."
            ),
            'trade_rule': (
                "→ Price > Pivot: Bullish bias for today's session.\n"
                "→ Price at S1 or below: Strong buy zone (support).\n"
                "→ Price at R1 or above: Strong sell zone (resistance).\n"
                "→ Use pivot levels as intraday targets for Bulkowski patterns."
            ),
        })

    # ── 10. INTERNAL BAR STRENGTH (IBS) — Ch.4.4 ─────────────────────────────
    # IBS = (Close - Low) / (High - Low)
    # IBS near 0 = closed near low = oversold → BUY
    # IBS near 1 = closed near high = overbought → SELL
    last_bar = df.iloc[-1]
    bar_range = last_bar['High'] - last_bar['Low']
    if bar_range > 0:
        ibs = (last_bar['Close'] - last_bar['Low']) / bar_range
    else:
        ibs = 0.5

    # Rolling IBS to get context
    if n >= 5:
        ibs_series = (df['Close'] - df['Low']) / (df['High'] - df['Low']).replace(0, np.nan)
        ibs_series = ibs_series.fillna(0.5)
        ibs_5d_avg = ibs_series.iloc[-5:].mean()
    else:
        ibs_5d_avg = ibs

    if ibs <= 0.20:
        ibs_signal = 'DEEPLY OVERSOLD'
        ibs_color  = '#2ecc71'; ibs_icon = '▲'; ibs_str = 88
        ibs_note   = 'Closed near day low. Strong mean-reversion buy signal.'
    elif ibs <= 0.35:
        ibs_signal = 'OVERSOLD'
        ibs_color  = '#27ae60'; ibs_icon = '▲'; ibs_str = 65
        ibs_note   = 'Closed in lower third. Mild buy signal.'
    elif ibs >= 0.80:
        ibs_signal = 'DEEPLY OVERBOUGHT'
        ibs_color  = '#e74c3c'; ibs_icon = '▼'; ibs_str = 88
        ibs_note   = 'Closed near day high. Strong mean-reversion sell signal.'
    elif ibs >= 0.65:
        ibs_signal = 'OVERBOUGHT'
        ibs_color  = '#e67e22'; ibs_icon = '▼'; ibs_str = 65
        ibs_note   = 'Closed in upper third. Mild sell signal.'
    else:
        ibs_signal = 'NEUTRAL'
        ibs_color  = '#7f8c8d'; ibs_icon = '◆'; ibs_str = 25
        ibs_note   = 'Closed in middle of range. No IBS signal.'

    signals.append({
        'name'   : 'Internal Bar Strength (IBS)',
        'source' : 'Kakushadze Ch.4.4',
        'signal' : ibs_signal,
        'icon'   : ibs_icon,
        'color'  : ibs_color,
        'value'  : f"IBS = {ibs:.3f}  (0=near low, 1=near high)  |  5d avg IBS = {ibs_5d_avg:.3f}",
        'strength': ibs_str,
        'desc'   : (
            f"Internal Bar Strength:\n"
            f"  IBS = (Close - Low) / (High - Low)\n"
            f"  Today's IBS = ({last_bar['Close']:.2f} - {last_bar['Low']:.2f}) "
            f"/ ({last_bar['High']:.2f} - {last_bar['Low']:.2f}) = {ibs:.3f}\n"
            f"  5-day average IBS = {ibs_5d_avg:.3f}\n\n"
            f"  {ibs_note}\n\n"
            f"Kakushadze (Ch.4.4): IBS near 0 = closed near low = cheap (buy).\n"
            f"IBS near 1 = closed near high = rich (sell).\n"
            f"Most powerful as a next-day mean-reversion signal."
        ),
        'trade_rule': (
            "→ IBS ≤ 0.20: Strong buy next open. Price closed near day's low.\n"
            "   Confirms bullish Bulkowski patterns strongly.\n"
            "→ IBS ≥ 0.80: Strong sell next open. Price closed near day's high.\n"
            "   Confirms bearish Bulkowski patterns strongly.\n"
            "→ IBS between 0.35–0.65: No IBS signal — ignore."
        ),
    })

    # ── 11. TREND FOLLOWING SIGNAL — Ch.10.4 ─────────────────────────────────
    # Signal = sign(P(t) - P(t-n)) for multiple lookbacks
    # Position size proportional to trend strength
    tf_results = []
    for lb in [5, 10, 20, 60]:
        if n > lb:
            past_price = close.iloc[-(lb+1)]
            ret = (current_price - past_price) / past_price * 100
            tf_results.append((lb, ret))

    if tf_results:
        bull_count = sum(1 for _, r in tf_results if r > 0)
        bear_count = sum(1 for _, r in tf_results if r < 0)
        avg_ret    = np.mean([r for _, r in tf_results])
        # Trend strength = proportion of lookbacks agreeing
        agreement  = max(bull_count, bear_count) / len(tf_results) * 100

        if bull_count > bear_count:
            tf_signal = f'TRENDING UP ({bull_count}/{len(tf_results)} agree)'
            tf_color  = '#2ecc71'; tf_icon = '▲'
        elif bear_count > bull_count:
            tf_signal = f'TRENDING DOWN ({bear_count}/{len(tf_results)} agree)'
            tf_color  = '#e74c3c'; tf_icon = '▼'
        else:
            tf_signal = 'NO CLEAR TREND'
            tf_color  = '#7f8c8d'; tf_icon = '◆'

        tf_str = int(agreement)
        tf_lines = '\n'.join([f"  {lb:3d}-day return: {r:+.2f}%  {'↑' if r>0 else '↓'}"
                               for lb, r in tf_results])

        signals.append({
            'name'   : 'Trend Following (Multi-lookback)',
            'source' : 'Kakushadze Ch.10.4',
            'signal' : tf_signal,
            'icon'   : tf_icon,
            'color'  : tf_color,
            'value'  : f"Avg return across lookbacks: {avg_ret:+.2f}%  |  Agreement: {agreement:.0f}%",
            'strength': tf_str,
            'desc'   : (
                f"Trend Following — Multiple Lookback Periods:\n"
                f"{tf_lines}\n\n"
                f"Agreement across all periods: {agreement:.0f}%\n\n"
                f"Kakushadze (Ch.10.4): Signal = sign(Price(t) - Price(t-n)).\n"
                f"Position size ∝ momentum strength.\n"
                f"Cut losses fast, let winners run."
            ),
            'trade_rule': (
                "→ All 4 lookbacks positive: Strong trend up. Size up on longs.\n"
                "→ All 4 lookbacks negative: Strong trend down. Size up on shorts.\n"
                "→ Mixed signals: No trend. Reduce position size 50%.\n"
                "→ Best when 60-day trend agrees with 5-day and 10-day trend."
            ),
        })

    # ── 12. INTERNAL BAR STRENGTH MOMENTUM (DUAL MOMENTUM) — Ch.4.1 ──────────
    # Combines cumulative return (momentum) with MA filter
    # Buy only if: top momentum AND price > MA(200)
    if n >= 22:
        ret_1m = (current_price - close.iloc[-22]) / close.iloc[-22] * 100
        ret_3m_val = close.iloc[max(0, n-63)]
        ret_3m = (current_price - ret_3m_val) / ret_3m_val * 100 if ret_3m_val > 0 else 0
        above_ma200 = current_price > sma200

        # Dual momentum: both time-series momentum AND above MA200
        pos_mom  = ret_1m > 0 and ret_3m > 0
        dual_ok  = pos_mom and above_ma200
        neg_mom  = ret_1m < 0 and ret_3m < 0
        dual_neg = neg_mom and not above_ma200

        if dual_ok:
            dm_signal = 'DUAL BULL — FULL LONG'
            dm_color  = '#2ecc71'; dm_icon = '▲▲'; dm_str = 92
        elif pos_mom and not above_ma200:
            dm_signal = 'MOM OK — MA FILTER BLOCKS'
            dm_color  = '#f39c12'; dm_icon = '◆'; dm_str = 45
        elif above_ma200 and not pos_mom:
            dm_signal = 'ABOVE MA — MOM WEAK'
            dm_color  = '#3498db'; dm_icon = '◆'; dm_str = 45
        elif dual_neg:
            dm_signal = 'DUAL BEAR — FULL SHORT'
            dm_color  = '#e74c3c'; dm_icon = '▼▼'; dm_str = 92
        else:
            dm_signal = 'MIXED — REDUCE SIZE'
            dm_color  = '#7f8c8d'; dm_icon = '◆'; dm_str = 30

        signals.append({
            'name'   : 'Dual Momentum Filter',
            'source' : 'Kakushadze Ch.4.1',
            'signal' : dm_signal,
            'icon'   : dm_icon,
            'color'  : dm_color,
            'value'  : (f"1m return: {ret_1m:+.1f}%  |  3m return: {ret_3m:+.1f}%  |  "
                        f"Price vs MA200: {'ABOVE' if above_ma200 else 'BELOW'}"),
            'strength': dm_str,
            'desc'   : (
                f"Dual Momentum (Antonacci / Kakushadze Ch.4.1):\n"
                f"  1-month return:  {ret_1m:+.2f}%\n"
                f"  3-month return:  {ret_3m:+.2f}%\n"
                f"  Price vs MA200:  {'ABOVE ✅' if above_ma200 else 'BELOW ❌'}\n\n"
                f"Rule: Buy ONLY if both momentum periods are positive AND\n"
                f"price is above the 200-day MA. All three must agree.\n"
                f"If MA filter blocks: hold cash or defensive position."
            ),
            'trade_rule': (
                "→ DUAL BULL: All conditions met. Full position size on longs.\n"
                "→ MA Filter blocks: Stay in cash or defensive. Do not fight.\n"
                "→ DUAL BEAR: Full position size on shorts.\n"
                "→ This is the single strongest combined entry filter in this app."
            ),
        })

    # ── 13. RETURN SKEWNESS — Ch.9.5 ─────────────────────────────────────────
    # Negative skewness in past returns = higher future returns expected
    # Negative corr between past skewness and future returns (Kakushadze)
    sk_period = min(60, n - 1)
    if sk_period >= 10:
        ret_series = close.pct_change().dropna().iloc[-sk_period:]
        r_mean = ret_series.mean()
        r_std  = ret_series.std()
        if r_std > 0:
            skewness = ((ret_series - r_mean) ** 3).mean() / (r_std ** 3)
        else:
            skewness = 0.0

        if skewness <= -0.5:
            sk_signal = 'NEGATIVE SKEW — BULLISH'
            sk_color  = '#2ecc71'; sk_icon = '▲'; sk_str = 70
            sk_note   = 'Negative skew → higher future returns expected (Kakushadze Ch.9.5).'
        elif skewness >= 0.5:
            sk_signal = 'POSITIVE SKEW — BEARISH'
            sk_color  = '#e74c3c'; sk_icon = '▼'; sk_str = 70
            sk_note   = 'Positive skew → lower future returns expected.'
        else:
            sk_signal = 'NEUTRAL SKEW'
            sk_color  = '#7f8c8d'; sk_icon = '◆'; sk_str = 25
            sk_note   = 'Skewness near zero. No directional signal.'

        signals.append({
            'name'   : 'Return Skewness',
            'source' : 'Kakushadze Ch.9.5',
            'signal' : sk_signal,
            'icon'   : sk_icon,
            'color'  : sk_color,
            'value'  : f"60-day return skewness = {skewness:.3f}",
            'strength': sk_str,
            'desc'   : (
                f"Return Skewness (60-day window):\n"
                f"  Skewness = {skewness:.3f}\n\n"
                f"  {sk_note}\n\n"
                f"Kakushadze (Ch.9.5): Empirically, negative skewness in\n"
                f"historical returns is associated with higher FUTURE returns.\n"
                f"Positive skewness = lower future returns on average.\n"
                f"The market 'penalizes' positive skew (lottery-like assets)."
            ),
            'trade_rule': (
                "→ Skewness ≤ -0.5: Confirms bullish setups — statistically higher returns ahead.\n"
                "→ Skewness ≥ +0.5: Warns against long setups — statistically lower returns ahead.\n"
                "→ Best used as a SECONDARY confirmation filter, not primary signal.\n"
                "→ Combine with Z-Score: negative skew + oversold Z-score = strong buy."
            ),
        })

    # ── 14. RISK-ADJUSTED MOMENTUM — Ch.3.1 VARIANT ──────────────────────────
    # R_risk_adj = R_cumulative / σ  (Sharpe-like momentum)
    # Better than raw momentum — removes vol bias
    if n > 22:
        ra_period = min(252, n - 2)
        ra_skip   = min(21, n - 2)
        p_start   = close.iloc[max(0, n - ra_period)]
        p_end     = close.iloc[max(0, n - ra_skip)]
        raw_ret   = (p_end - p_start) / p_start * 100 if p_start > 0 else 0
        ret_vol   = close.pct_change().iloc[-ra_period:].std() * (252**0.5) * 100
        ra_mom    = raw_ret / ret_vol if ret_vol > 0 else 0

        if ra_mom >= 1.0:
            ra_signal = 'STRONG RISK-ADJ MOMENTUM'
            ra_color  = '#2ecc71'; ra_icon = '▲'; ra_str = 80
        elif ra_mom >= 0.3:
            ra_signal = 'POSITIVE RISK-ADJ MOM'
            ra_color  = '#27ae60'; ra_icon = '▲'; ra_str = 55
        elif ra_mom <= -1.0:
            ra_signal = 'STRONG NEGATIVE R-ADJ MOM'
            ra_color  = '#e74c3c'; ra_icon = '▼'; ra_str = 80
        elif ra_mom <= -0.3:
            ra_signal = 'NEGATIVE RISK-ADJ MOM'
            ra_color  = '#e67e22'; ra_icon = '▼'; ra_str = 55
        else:
            ra_signal = 'NEUTRAL'
            ra_color  = '#7f8c8d'; ra_icon = '◆'; ra_str = 20

        signals.append({
            'name'   : 'Risk-Adjusted Momentum',
            'source' : 'Kakushadze Ch.3.1 variant',
            'signal' : ra_signal,
            'icon'   : ra_icon,
            'color'  : ra_color,
            'value'  : (f"R_adj = {ra_mom:+.3f}  "
                        f"(Raw return: {raw_ret:+.1f}%  /  Ann.Vol: {ret_vol:.1f}%)"),
            'strength': ra_str,
            'desc'   : (
                f"Risk-Adjusted Momentum (Kakushadze Ch.3.1):\n"
                f"  Formula: R_adj = Cumulative Return / Annualised Volatility\n"
                f"  Raw return (12m, skip 1m): {raw_ret:+.2f}%\n"
                f"  Annualised volatility:     {ret_vol:.2f}%\n"
                f"  R_adj = {ra_mom:+.3f}\n\n"
                f"This is a Sharpe-like momentum measure. It penalises\n"
                f"high-volatility instruments making the same raw return\n"
                f"as a low-volatility one. More reliable than raw momentum."
            ),
            'trade_rule': (
                "→ R_adj ≥ 1.0: High quality momentum. Full position size.\n"
                "→ R_adj 0.3–1.0: Moderate. Standard position size.\n"
                "→ R_adj ≤ -1.0: Strong negative. Prefer shorts.\n"
                "→ Compare with simple Price Momentum — if both agree, higher confidence."
            ),
        })

    # ── 15. MULTI-ASSET TREND WITH VOL WEIGHTING — Ch.4.6 ────────────────────
    # w_i ∝ R_cum / σ_i  (momentum divided by volatility = vol-adjusted trend)
    # Gives a composite score combining direction and efficiency
    if n > 22:
        vol_20   = close.pct_change().iloc[-20:].std() * (252**0.5) * 100
        ret_20   = (current_price - close.iloc[-21]) / close.iloc[-21] * 100
        vol_wt   = ret_20 / vol_20 if vol_20 > 0 else 0  # Eq.4.12 equivalent

        if vol_wt >= 0.5:
            vw_signal = 'STRONG VOL-WEIGHTED BULL'
            vw_color  = '#2ecc71'; vw_icon = '▲'; vw_str = 78
        elif vol_wt >= 0.1:
            vw_signal = 'MILD VOL-WEIGHTED BULL'
            vw_color  = '#27ae60'; vw_icon = '▲'; vw_str = 50
        elif vol_wt <= -0.5:
            vw_signal = 'STRONG VOL-WEIGHTED BEAR'
            vw_color  = '#e74c3c'; vw_icon = '▼'; vw_str = 78
        elif vol_wt <= -0.1:
            vw_signal = 'MILD VOL-WEIGHTED BEAR'
            vw_color  = '#e67e22'; vw_icon = '▼'; vw_str = 50
        else:
            vw_signal = 'FLAT'
            vw_color  = '#7f8c8d'; vw_icon = '◆'; vw_str = 20

        signals.append({
            'name'   : 'Vol-Weighted Trend Score',
            'source' : 'Kakushadze Ch.4.6  Eq.4.12',
            'signal' : vw_signal,
            'icon'   : vw_icon,
            'color'  : vw_color,
            'value'  : (f"Score = {vol_wt:+.3f}  "
                        f"(20d return {ret_20:+.1f}% / 20d Ann.Vol {vol_20:.1f}%)"),
            'strength': vw_str,
            'desc'   : (
                f"Vol-Weighted Trend (Kakushadze Ch.4.6, Eq.4.12):\n"
                f"  Score = 20-day return / 20-day annualised volatility\n"
                f"  20-day return: {ret_20:+.2f}%\n"
                f"  20-day ann. vol: {vol_20:.2f}%\n"
                f"  Vol-weighted score: {vol_wt:+.3f}\n\n"
                f"From Kakushadze's multi-asset trend following:\n"
                f"w_i ∝ R_cum / σ_i (Eq.4.12). This is a position sizing\n"
                f"guide — higher score = larger position justified."
            ),
            'trade_rule': (
                "→ Score ≥ +0.5: Strong bull trend relative to vol. Buy with confidence.\n"
                "→ Score ≤ -0.5: Strong bear trend relative to vol. Short with confidence.\n"
                "→ Score near 0: Choppy. Reduce size or wait.\n"
                "→ Use as position sizing guide: score × base_size = actual size."
            ),
        })

    return signals


def compute_combined_score(quant_signals, pattern_direction):
    """
    Compute an overall combined confidence score:
    - Counts how many quant signals agree with the pattern direction
    - Returns score 0-100 and a verdict string
    """
    if not quant_signals or not pattern_direction:
        return 50, 'INSUFFICIENT DATA'

    is_bullish = 'BULL' in pattern_direction.upper()
    agree      = 0
    disagree   = 0
    neutral    = 0

    bullish_words = {'BULL', 'ABOVE', 'GOLDEN', 'OVERSOLD', 'MOMENTUM', 'LOW VOL',
                     'UPPER', 'BREAKOUT HIGH', 'POSITIVE', 'STRONG MOM', 'ALIGNED',
                     'SUPPORT', 'TRENDING UP', 'NEGATIVE SKEW', 'DUAL BULL',
                     'VOL-WEIGHTED BULL', 'RISK-ADJ MOM'}
    bearish_words = {'BEAR', 'BELOW', 'DEATH', 'OVERBOUGHT', 'NEGATIVE',
                     'BREAKOUT LOW', 'LOWER', 'STRONG NEG', 'RESISTANCE',
                     'TRENDING DOWN', 'POSITIVE SKEW', 'DUAL BEAR',
                     'VOL-WEIGHTED BEAR'}

    for sig in quant_signals:
        s = sig['signal'].upper()
        is_bull_sig = any(w in s for w in bullish_words)
        is_bear_sig = any(w in s for w in bearish_words)

        if is_bullish:
            if is_bull_sig:   agree    += 1
            elif is_bear_sig: disagree += 1
            else:             neutral  += 1
        else:
            if is_bear_sig:   agree    += 1
            elif is_bull_sig: disagree += 1
            else:             neutral  += 1

    total = len(quant_signals)
    agree_pct = agree / total * 100

    if agree_pct >= 75:
        verdict = 'STRONG CONFIRMATION'
        verdict_color = '#2ecc71'
    elif agree_pct >= 50:
        verdict = 'MODERATE CONFIRMATION'
        verdict_color = '#f1c40f'
    elif agree_pct >= 25:
        verdict = 'WEAK / MIXED'
        verdict_color = '#e67e22'
    else:
        verdict = 'SIGNALS CONFLICT'
        verdict_color = '#e74c3c'

    return round(agree_pct), verdict, verdict_color, agree, disagree, neutral



# ─────────────────────────────────────────────────────────────────────────────
#  AL BROOKS PRICE ACTION ENGINE
#  Source: Trading Price Action Trends — Al Brooks (Wiley, 2012)
#  All signals computed purely from OHLC data
#  Only strategies detectable from price bars included (no indicators needed
#  except the 20-EMA which is calculated here from Close prices)
# ─────────────────────────────────────────────────────────────────────────────

BROOKS_DB = {

    "Breakout Pullback": {
        "type": "continuation", "direction": "with-trend",
        "source": "Brooks Ch.3 / Ch.12",
        "first_principle": (
            "Most breakouts fail — but those that succeed almost always pull back "
            "before continuing. The pullback is the market testing the breakout level. "
            "When it holds, it proves the breakout was genuine. This is how strong "
            "trends work: breakout → pullback → continuation."
        ),
        "identification": [
            "A clear breakout above a significant level (swing high, resistance, channel top)",
            "Breakout bar is a strong trend bar — large body, small tails, closes near high",
            "Price pulls back 2–5 bars after the breakout — bars should be small, tight, overlapping",
            "Pullback did NOT break back below the breakout point — level holds as support",
            "A signal bar forms at or near the breakout level (bull bar for long)",
            "Always-in direction is bullish — HTF context confirms",
        ],
        "trading_plan": {
            "entry": "Stop order 1 tick ABOVE the signal bar high at the pullback level",
            "stop":  "1 tick below the signal bar low (or below the pullback swing low)",
            "target_1": "Measured move = breakout bar height × 2 — scale 50% here",
            "target_2": "Next swing high / prior resistance level — scale 30%",
            "target_3": "Full measured move from breakout level — 20% runner",
            "manage": "After T1: move stop to breakeven. Trail below each new swing low.",
            "avoid": "Large opposing bars in the pullback = breakout likely failed. Skip.",
        },
        "edge": "Requires two proofs: (1) enough force to break a level, (2) that level held on retest. Two confirmations, one entry.",
    },

    "High 1 / High 2 Pullback": {
        "type": "continuation", "direction": "bullish",
        "source": "Brooks Glossary / Ch.20",
        "first_principle": (
            "High 2 fires after weak bulls and weak bears are both shaken out. "
            "The first attempt (High 1) shakes out weak bulls. The second (High 2) "
            "triggers with institutional buying. Two categories of trapped traders "
            "covering simultaneously = explosive move."
        ),
        "identification": [
            "Bull trend confirmed: higher highs + higher lows, price above 20 EMA",
            "A pullback of 2–10 bars has occurred after a with-trend move",
            "High 2 preferred over High 1 — second attempt more reliable",
            "Signal bar has a bull body — closes above open",
            "Signal bar NOT heavily overlapping with many prior bars",
            "Pullback bars are mostly small-bodied — shows weak selling",
            "20 EMA is nearby or below — institutional support present",
        ],
        "trading_plan": {
            "entry": "Stop order 1 tick ABOVE the High 2 signal bar high",
            "stop":  "1 tick below the signal bar low (or below the pullback swing low)",
            "target_1": "Prior swing high — scale 50%",
            "target_2": "Measured move from pullback low — scale 30%",
            "target_3": "Trend channel line extension — 20% runner",
            "manage": "After T1: move stop below the pullback low. Trail below new swing lows.",
            "avoid": "Large bear bars in the pullback = sellers are strong, not just cleanup. Skip.",
        },
        "edge": "High 2 at the 20 EMA during a bull flag is one of the simplest and most reliable Brooks setups.",
    },

    "Two-Bar Reversal": {
        "type": "reversal", "direction": "both",
        "source": "Brooks Ch.6",
        "first_principle": (
            "Two consecutive bars where the first is a strong trend bar and the second "
            "is a strong bar in the opposite direction. On any higher timeframe these "
            "two bars form a single reversal bar. Proves momentum was immediately and "
            "completely reversed — the most direct evidence of control shift."
        ),
        "identification": [
            "Bar 1: large trend bar (e.g. large bull bar) — the setup bar",
            "Bar 2: large opposite trend bar (large bear bar) closing near its low",
            "Both bars significantly overlap each other",
            "Two-bar reversal occurs at meaningful level: swing high, resistance, channel line",
            "Context: after prolonged trend OR multiple climax bars",
            "Signal bar closes in bottom 25% of range — shows bear dominance",
        ],
        "trading_plan": {
            "entry": "SHORT: stop 1 tick below bar 2 low. LONG: stop 1 tick above bar 2 high.",
            "stop":  "Above the HIGHER of the two bars (bar 1 high for short entry)",
            "target_1": "Test of the 20-bar EMA — scale 50%",
            "target_2": "Prior swing low / next support — scale 30%",
            "target_3": "Two-legged correction: measure first leg, project equal second — 20%",
            "manage": "After T1: move stop above the swing high between entry and T1.",
            "avoid": "Large with-trend bar immediately after entry = exit at breakeven. Pattern may have failed.",
        },
        "edge": "Strongest after sell climaxes — 3+ consecutive large bear bars. The trapped traders from bar 1 are your fuel.",
    },

    "Wedge Reversal": {
        "type": "reversal", "direction": "both",
        "source": "Brooks Ch.14 / Ch.21",
        "first_principle": (
            "Three pushes in one direction where each push is smaller than the last. "
            "Diminishing thrust proves buyers are losing power. Each successive high "
            "requires more effort and produces a smaller result — structural exhaustion. "
            "Three pushes = three failed attempts to maintain momentum."
        ),
        "identification": [
            "Three clear pushes in one direction visible on the chart",
            "Each successive push is smaller than prior — converging, diminishing",
            "Third push ideally overshoots the trend channel line (climactic overshoot)",
            "Strong reversal bar on third push: bear body, close near low (for wedge top)",
            "Context: occurs at significant resistance level or trend channel line",
            "Second entry preferred — first reversal attempt fails, second more reliable",
        ],
        "trading_plan": {
            "entry": "Stop 1 tick BELOW the reversal bar low on third push (wedge top = short)",
            "stop":  "Above the high of the third push",
            "target_1": "Bottom of the wedge channel (start of push 3) — scale 50%",
            "target_2": "Start of the channel (push 1 low) — scale 30%",
            "target_3": "Start of the entire trend — 20% runner if major reversal",
            "manage": "After T1: move stop to above entry bar high. Scale at each push low.",
            "avoid": "Wedge in a very strong trend = correction only, not major reversal. Reduce size.",
        },
        "edge": "Combines three evidences: diminishing momentum, climactic overshoot, trapped traders on third push. All three at once.",
    },

    "Failed Breakout Fade": {
        "type": "reversal", "direction": "both",
        "source": "Brooks Ch.3 / Ch.12",
        "first_principle": (
            "Most breakouts fail. When price breaks a widely-watched level it triggers "
            "buy stops AND attracts sellers who see the level as overvalued. If sellers "
            "immediately overwhelm new buyers, the breakout bar reverses — creating a "
            "trap. Trapped buyers must sell to exit. Their exit = your fuel."
        ),
        "identification": [
            "A clear breakout above a significant level occurred (swing high, channel top)",
            "Within 1–5 bars price reverses BACK below the breakout level",
            "Reversal bar closes BELOW the breakout level — full body close, not just wick",
            "Original breakout had weak follow-through: small body, large tail, or immediate reversal",
            "Context: near the top of a trading range OR always-in direction is bear",
            "No large bull bars appear after the reversal — confirms the fade",
        ],
        "trading_plan": {
            "entry": "Short stop 1 tick BELOW the reversal signal bar low",
            "stop":  "Above the HIGH of the failed breakout bar (original breakout candle)",
            "target_1": "Opposite extreme of the trading range — scale 50%",
            "target_2": "Measured move = height of range below the bottom — scale 30%",
            "target_3": "Trend continuation if always-in is bear — 20%",
            "manage": "After T1: move stop to breakeven. 'Failed failure' = cover shorts, go long.",
            "avoid": "If market makes new high beyond failed breakout after entry: exit immediately.",
        },
        "edge": "Brooks: 'Most breakouts fail.' This is the statistically correct trade. The trapped bulls become your fuel after the reversal bar closes back inside the range.",
    },

    "Measured Move Projection": {
        "type": "continuation", "direction": "with-trend",
        "source": "Brooks Ch.20 / Ch.21",
        "first_principle": (
            "Markets move in symmetrical waves because the same institutional forces "
            "that drove leg 1 are still present and will drive leg 2 the same distance. "
            "If an institution bought X size in leg 1 and is still committed, they buy "
            "X size in leg 2, moving price the same distance. Measured moves are the "
            "structural signature of consistent institutional intent."
        ),
        "identification": [
            "A clear two-leg structure visible: Leg 1 move → correction → Leg 2 beginning",
            "Leg 2 has begun in same direction as Leg 1 with with-trend momentum",
            "Measured move target is at a significant resistance/support level",
            "No large opposing trend bars developing as price approaches target",
            "Correction between legs was 30–60% of leg 1 (healthy retracement)",
        ],
        "trading_plan": {
            "entry": "Enter at start of Leg 2: buy the pullback after Leg 1 completes (High 2 or breakout pullback)",
            "stop":  "Below the entry signal bar low (Leg 2 entry stop)",
            "target_1": "Measured move = Leg 1 length added to start of Leg 2 — scale 60%",
            "target_2": "If target aligns with prior swing high: stronger resistance, scale 80%",
            "target_3": "If momentum blows past target: new measured move from current correction",
            "manage": "Hold through noise between entry and target. At target: watch for reversal.",
            "avoid": "If correction exceeds 60% of leg 1 — move may not resume. Skip.",
        },
        "edge": "75% accuracy for achieving the equal-leg target. Use as a TARGET TOOL for all other setups — marks the most probable exit zone.",
    },

    "Moving Average Gap Bar": {
        "type": "continuation", "direction": "bullish",
        "source": "Brooks Glossary / Ch.19",
        "first_principle": (
            "When a pullback in a strong bull trend produces a bar that does not even "
            "touch the 20-bar EMA, the trend is so strong that the normal pullback test "
            "has not occurred. The market is propelled so aggressively that the moving "
            "average acts as a resistance floor — buyers overwhelm sellers before price "
            "even reaches the average."
        ),
        "identification": [
            "Strong bull trend: price well above 20 EMA, EMA sloping up, multiple bull bars",
            "A pullback begins but the HIGH of the pullback bar does NOT touch the 20 EMA",
            "The gap bar itself is NOT a large bear bar — should be doji, small, or inside bar",
            "Market reverses before reaching EMA and prints a with-trend signal bar",
            "Always-in direction unambiguously long — no major trend line break occurred",
            "EMA is still rising — flat EMA = weaker setup",
        ],
        "trading_plan": {
            "entry": "Stop 1 tick ABOVE the signal bar high that forms after the gap bar",
            "stop":  "1 tick below the LOW of the gap bar",
            "target_1": "Test of prior swing high / trend extreme — scale 50%",
            "target_2": "Measured move = prior impulse leg distance from gap bar reversal — scale 30%",
            "target_3": "Trend channel line extension — 20% runner",
            "manage": "After T1: move stop to below gap bar low. Strong trend — swing 60–70%.",
            "avoid": "Any bar that closes BELOW the 20 EMA: trend may be changing — exit or tighten.",
        },
        "edge": "The gap bar reversal often precedes the longest leg of the entire trend. Institutions were so aggressive they bought before price could even reach the EMA.",
    },

    "Inside Bar / ii Breakout Mode": {
        "type": "continuation", "direction": "breakout",
        "source": "Brooks Ch.12 / Ch.4",
        "first_principle": (
            "An inside bar represents a complete stalemate — bulls cannot break above "
            "prior high, bears cannot break below prior low. The stalemate is unstable. "
            "One side is quietly accumulating. When it breaks, trapped participants "
            "are squeezed and their covering amplifies the move. ii = doubled stalemate "
            "= even more explosive breakout."
        ),
        "identification": [
            "An inside bar has formed: high ≤ prior bar high, low ≥ prior bar low",
            "Ideally a second inside bar within the first (ii pattern) — doubled energy",
            "Bars in the range are small and overlapping — genuine equilibrium",
            "No large opposing trend bars in the immediate vicinity",
            "HTF context gives a bias: if daily is in bull trend, favor the long breakout",
        ],
        "trading_plan": {
            "entry": "Buy stop 1 tick ABOVE first inside bar high AND sell stop 1 tick BELOW first inside bar low. First triggered = entry. Cancel the other.",
            "stop":  "Long triggered: stop 1 tick below ii low. Short triggered: stop 1 tick above ii high.",
            "target_1": "Measured move = height of the ii range × 2 — scale 50%",
            "target_2": "Prior swing high (upward) or low (downward) — scale 30%",
            "target_3": "If trend day forms: hold for full trend target trailing swing lows — 20%",
            "manage": "After T1: move stop to breakeven. Failed breakout of ii = fade in opposite direction.",
            "avoid": "Failed breakout from ii: the failed direction is a stronger signal — fade immediately.",
        },
        "edge": "The ii pattern is the purest breakout mode setup. Two bars of complete stalemate = maximum energy compression. First triggered stop is your entry — let the market tell you the direction.",
    },

    "Final Flag Reversal": {
        "type": "reversal", "direction": "bearish",
        "source": "Brooks Ch.21 / Ch.16",
        "first_principle": (
            "A final flag appears to be just another continuation flag but is actually "
            "the last pause before a major reversal. The market has exhausted itself but "
            "most traders haven't noticed. They buy the breakout — and are immediately "
            "trapped. All those late buyers become the selling fuel for the reversal."
        ),
        "identification": [
            "A prolonged bull trend in place — multiple legs up, extended channel, 3+ pushes",
            "A small tight trading range forms near the top: 3–7 overlapping bars, small bodies",
            "The flag appears to be a safe continuation setup — this is what makes it a trap",
            "Breakout of the flag (upside in bull trend) FAILS within 1–5 bars",
            "A bear reversal bar forms after the failed breakout: close near the low",
            "Context: at or near trend channel line, measured move target, or major resistance",
        ],
        "trading_plan": {
            "entry": "Short stop 1 tick BELOW the signal bar low after flag breakout fails",
            "stop":  "Above the HIGH of the failed breakout bar",
            "target_1": "Start of the final leg up (start of the spike or last channel leg) — scale 50%",
            "target_2": "Start of the entire channel (bottom of the bull channel) — scale 30%",
            "target_3": "Measured move down equal to height of bull channel — 20% runner",
            "manage": "After T1: move stop to breakeven. First bounce after reversal = bear flag. Short that bounce too.",
            "avoid": "If market makes new high beyond the failed breakout: exit — trend has resumed.",
        },
        "edge": "The most dangerous trap in trend trading — looks exactly like a safe continuation. The failed breakout is the confirmation. Can generate 3–5x the profit of a normal trade.",
    },

    "Spike and Channel": {
        "type": "continuation", "direction": "with-trend",
        "source": "Brooks Ch.21",
        "first_principle": (
            "Every trend has two phases: a Spike (fast, one-sided, everyone agrees) "
            "and a Channel (slower, two-sided, both sides trade but one still dominates). "
            "Understanding which phase you are in determines your strategy completely — "
            "swing with the spike, scalp/swing channel pullbacks."
        ),
        "identification": [
            "A clear spike of 2+ strong trend bars with minimal overlap formed recently",
            "Price is now in a channel phase: overlapping bars, smaller pullbacks, slower slope",
            "Looking to buy pullbacks (bull channel) or sell rallies (bear channel) — only with-trend",
            "Price has pulled back to the lower channel line (bull) or upper channel line (bear)",
            "A with-trend signal bar exists at the channel line",
            "No more than 3 pushes completed — if 3 done, channel may be ending",
        ],
        "trading_plan": {
            "entry": "Stop 1 tick ABOVE signal bar at the channel line (for longs in bull channel)",
            "stop":  "1 tick below the signal bar low. If large: below nearest swing low in pullback.",
            "target_1": "Prior swing high in the channel (top of channel line) — scalp 50%",
            "target_2": "Measured move = spike length added to start of channel — 30%",
            "target_3": "Three pushes complete — exit all, expect channel reversal — 20%",
            "manage": "After T1: move stop to entry. Do NOT trade countertrend in the channel.",
            "avoid": "Countertrend scalps in a strong channel — this is the most costly mistake.",
        },
        "edge": "During the channel, every failed countertrend attempt provides the with-trend entry signal. The trapped countertrend traders are your fuel.",
    },

    "Trend Line Break and Lower High": {
        "type": "reversal", "direction": "bearish",
        "source": "Brooks Ch.13",
        "first_principle": (
            "A trend line break is the FIRST sign of losing control. But it does NOT mean "
            "reversal — only that a correction is more likely. The full reversal requires: "
            "(1) break the major trend line, THEN (2) test the old extreme, THEN (3) fail "
            "at a lower high. This two-step process filters out 70%+ of false reversal signals."
        ),
        "identification": [
            "Step 1 complete: major bull trend line broken by a bar closing below it",
            "The break was meaningful — bar body closed below the line, not just a wick",
            "Step 2 forming: price rallying back toward the prior swing high",
            "The test of the old high forms a LOWER HIGH (fails to reach old extreme)",
            "A bear reversal bar forms at the lower high test",
            "HTF context confirms weakening",
        ],
        "trading_plan": {
            "entry": "Short stop 1 tick BELOW the signal bar low at the lower high test",
            "stop":  "Above the signal bar high (for the lower high test short)",
            "target_1": "Low of the trend line break bar (swing low created during the break) — scale 50%",
            "target_2": "Measured move = height of old trend projected downward — scale 30%",
            "target_3": "Start of the bull trend (origin point) — 20% runner for major reversal",
            "manage": "After T1: move stop to breakeven. Expect two legs down minimum.",
            "avoid": "Higher high made after entry = trend resumed, exit immediately.",
        },
        "edge": "Wait for the trend to TEST its old extreme after the break. The lower high IS the reversal signal with a defined stop. One of the most reliable setups in all of price action.",
    },

    "Trend from the Open": {
        "type": "continuation", "direction": "with-trend",
        "source": "Brooks Ch.23",
        "first_principle": (
            "On some days the market opens and immediately trends with almost no pullback. "
            "Institutions came in before the open with a clear directional mandate and execute "
            "aggressively. Every small pullback is immediately bought. This continues until "
            "the institutional mandate is fulfilled — often all day. Missing this day is "
            "the most expensive mistake."
        ),
        "identification": [
            "First bar is a large trend bar — closes in top/bottom 25% of its range",
            "Second bar continues in same direction without reversing",
            "By bar 5: no reversal, no meaningful pullback — always-in direction is clear",
            "The 20 EMA is being approached from one direction only",
            "Any pullbacks are 1–3 bars max, small, overlapping — not large bars",
            "Day type identified within first 15 minutes: Trend from the Open",
        ],
        "trading_plan": {
            "entry": "Enter ANY with-trend pullback that stalls — High 2, breakout pullback, MA gap bar",
            "stop":  "Below the signal bar low (bull day) / above signal bar high (bear day)",
            "target_1": "1× average bar size beyond entry — scalp 50%",
            "target_2": "Prior major swing level or measured move target — scale 30%",
            "target_3": "Hold remaining 20% ALL DAY trailing each pullback low — let it run",
            "manage": "After T1: trail stop by each successive pullback low. NEVER take countertrend trades on this day.",
            "avoid": "Any countertrend position on a trend from open day — exit immediately if wrong.",
        },
        "edge": "On strong trend days, swing part of every position. The single runner held from the first entry can be more profitable than 20 normal scalp trades. Scalp 50%, swing 50%.",
    },
}


def detect_brooks_signals(df):
    """
    Detect Al Brooks price action signals from OHLC data.
    Returns list of signal dicts with name, signal, confidence, entry, stop, target, desc.
    All computed purely from OHLC bars — no external data needed.
    """
    signals = []
    n = len(df)
    if n < 10:
        return signals

    closes = df['Close'].values
    highs  = df['High'].values
    lows   = df['Low'].values
    opens  = df['Open'].values
    current = closes[-1]

    # ── Compute 20-EMA from Close ──────────────────────────────────────────
    ema20_series = _ema(df['Close'], min(20, n-1))
    ema20 = ema20_series.iloc[-1]
    ema20_prev = ema20_series.iloc[-2] if n > 2 else ema20
    ema_rising = ema20 > ema20_prev

    # ── Bar classification helpers ─────────────────────────────────────────
    def bar_size(i):
        return highs[i] - lows[i]

    def is_bull_bar(i):
        return closes[i] > opens[i]

    def is_bear_bar(i):
        return closes[i] < opens[i]

    def body_pct(i):
        rng = bar_size(i)
        return abs(closes[i] - opens[i]) / rng if rng > 0 else 0

    def is_strong_bar(i, threshold=0.5):
        return body_pct(i) >= threshold

    avg_bar_size = np.mean([bar_size(i) for i in range(max(0,n-20), n)])

    # ── 1. INSIDE BAR / ii PATTERN ─────────────────────────────────────────
    if n >= 3:
        # Check last bar is inside prior bar
        ib1 = (highs[-1] <= highs[-2] and lows[-1] >= lows[-2])
        # Check ii: last two bars both inside the bar before them
        ib2 = (n >= 4 and
                highs[-2] <= highs[-3] and lows[-2] >= lows[-3] and
                highs[-1] <= highs[-2] and lows[-1] >= lows[-2])
        if ib1 or ib2:
            pattern = "ii Pattern" if ib2 else "Inside Bar"
            ib_high = highs[-3] if ib2 else highs[-2]
            ib_low  = lows[-3]  if ib2 else lows[-2]
            ib_range = ib_high - ib_low
            mm_target_up   = ib_high + ib_range * 2
            mm_target_down = ib_low  - ib_range * 2
            conf = 80 if ib2 else 65
            signals.append({
                'name'      : f"Brooks: {pattern} (Breakout Mode)",
                'source'    : "Brooks Ch.12",
                'signal'    : 'BREAKOUT MODE — BOTH SIDES',
                'icon'      : '◆',
                'color'     : '#f1c40f',
                'confidence': conf,
                'value'     : f"{'ii' if ib2 else 'i'} Range: {ib_low:.2f} – {ib_high:.2f}  |  Width: {ib_range:.2f}",
                'entry'     : f"BUY STOP: {ib_high + 0.01:.2f} (above {pattern} high)\nSELL STOP: {ib_low - 0.01:.2f} (below {pattern} low)",
                'stop'      : f"Long: {ib_low - 0.01:.2f}  |  Short: {ib_high + 0.01:.2f}",
                'target'    : f"T1 Up: {mm_target_up:.2f}  |  T1 Down: {mm_target_down:.2f}  (range × 2)",
                'desc'      : (
                    f"{pattern} detected on last {'2' if ib2 else '1'} bar(s).\n"
                    f"Range: {ib_low:.2f} – {ib_high:.2f} ({ib_range:.2f} pts)\n\n"
                    f"Brooks: Market is in BREAKOUT MODE. Place BOTH stops.\n"
                    f"First triggered = entry. Cancel the other immediately.\n"
                    f"{'ii = doubled energy — expect explosive breakout!' if ib2 else 'Single inside bar — moderate energy.'}"
                ),
            })

    # ── 2. TWO-BAR REVERSAL ────────────────────────────────────────────────
    if n >= 2:
        b1_bull = is_bull_bar(-2) and is_strong_bar(-2, 0.55)
        b2_bear = is_bear_bar(-1) and is_strong_bar(-1, 0.55)
        b1_bear = is_bear_bar(-2) and is_strong_bar(-2, 0.55)
        b2_bull = is_bull_bar(-1) and is_strong_bar(-1, 0.55)

        overlap_top    = min(highs[-1], highs[-2])
        overlap_bottom = max(lows[-1],  lows[-2])
        has_overlap = overlap_top > overlap_bottom

        # Bearish TBR: bull bar followed by bear bar
        if b1_bull and b2_bear and has_overlap:
            entry  = lows[-1]  - 0.01
            stop   = highs[-2] + 0.01
            risk   = stop - entry
            target = entry - risk * 2
            conf   = 72
            signals.append({
                'name'      : "Brooks: Two-Bar Reversal (Bearish)",
                'source'    : "Brooks Ch.6",
                'signal'    : '▼ BEARISH REVERSAL',
                'icon'      : '▼',
                'color'     : '#e74c3c',
                'confidence': conf,
                'value'     : f"Bar1(Bull)={closes[-2]:.2f}  Bar2(Bear)={closes[-1]:.2f}  Overlap: YES",
                'entry'     : f"SELL STOP: {entry:.2f} (1 tick below bar 2 low)",
                'stop'      : f"{stop:.2f} (above bar 1 high = {highs[-2]:.2f})",
                'target'    : f"T1: {closes[-2] - (closes[-2]-closes[-1]):.2f} (20 EMA area)  T2: {target:.2f}",
                'desc'      : (
                    f"Two-Bar Reversal TOP detected.\n"
                    f"Bar 1: Strong bull bar  Close={closes[-2]:.2f}\n"
                    f"Bar 2: Strong bear bar  Close={closes[-1]:.2f}\n"
                    f"Both bars overlap significantly.\n\n"
                    f"Brooks: This proves momentum was immediately and completely reversed.\n"
                    f"Trapped longs from bar 1 = your fuel. Risk = {risk:.2f} pts."
                ),
            })

        # Bullish TBR: bear bar followed by bull bar
        elif b1_bear and b2_bull and has_overlap:
            entry  = highs[-1] + 0.01
            stop   = lows[-2]  - 0.01
            risk   = entry - stop
            target = entry + risk * 2
            conf   = 72
            signals.append({
                'name'      : "Brooks: Two-Bar Reversal (Bullish)",
                'source'    : "Brooks Ch.6",
                'signal'    : '▲ BULLISH REVERSAL',
                'icon'      : '▲',
                'color'     : '#2ecc71',
                'confidence': conf,
                'value'     : f"Bar1(Bear)={closes[-2]:.2f}  Bar2(Bull)={closes[-1]:.2f}  Overlap: YES",
                'entry'     : f"BUY STOP: {entry:.2f} (1 tick above bar 2 high)",
                'stop'      : f"{stop:.2f} (below bar 1 low = {lows[-2]:.2f})",
                'target'    : f"T1: {ema20:.2f} (20 EMA)  T2: {target:.2f}  (2× risk)",
                'desc'      : (
                    f"Two-Bar Reversal BOTTOM detected.\n"
                    f"Bar 1: Strong bear bar  Close={closes[-2]:.2f}\n"
                    f"Bar 2: Strong bull bar  Close={closes[-1]:.2f}\n"
                    f"Both bars overlap significantly.\n\n"
                    f"Brooks: Trapped shorts from bar 1 = your fuel. Risk = {risk:.2f} pts."
                ),
            })

    # ── 3. MOVING AVERAGE GAP BAR ──────────────────────────────────────────
    # Pullback bar whose HIGH doesn't touch the 20 EMA (in a bull trend)
    if n >= 5 and ema_rising and current > ema20:
        # Check if recent bars show a pullback that didn't touch the EMA
        for i in range(-3, -1):
            if highs[i] < ema20 * 0.999:  # gap bar: high below EMA
                next_i = i + 1
                if next_i < 0 and is_bull_bar(next_i):  # signal bar after gap
                    entry  = highs[next_i] + 0.01
                    stop   = lows[i] - 0.01
                    risk   = entry - stop
                    target = entry + risk * 2
                    signals.append({
                        'name'      : "Brooks: MA Gap Bar (Strong Trend Re-Entry)",
                        'source'    : "Brooks Ch.19",
                        'signal'    : '▲ STRONG BULL TREND',
                        'icon'      : '▲▲',
                        'color'     : '#2ecc71',
                        'confidence': 78,
                        'value'     : f"20 EMA={ema20:.2f}  Gap bar high={highs[i]:.2f}  Gap={ema20-highs[i]:.2f} pts below EMA",
                        'entry'     : f"BUY STOP: {entry:.2f} (above signal bar after gap bar)",
                        'stop'      : f"{stop:.2f} (below gap bar low = {lows[i]:.2f})",
                        'target'    : f"T1: Prior swing high  T2: {target:.2f} (2× risk)",
                        'desc'      : (
                            f"MA Gap Bar detected — exceptional trend strength signal.\n"
                            f"20 EMA = {ema20:.2f}\n"
                            f"Pullback bar high = {highs[i]:.2f} (did NOT touch the EMA)\n"
                            f"Gap = {ema20-highs[i]:.2f} pts below EMA\n\n"
                            f"Brooks: Trend so strong that institutions bought before\n"
                            f"price even reached the average. This often precedes the\n"
                            f"longest leg of the entire trend."
                        ),
                    })
                break

    # ── 4. HIGH 2 / PULLBACK IN BULL TREND ────────────────────────────────
    if n >= 6 and current > ema20 and ema_rising:
        # Look for: consecutive bars making lower highs (pullback), then bar whose high > prior bar
        # Simple version: last 2 bars were lower, current bar breaks above prior bar
        pullback_bars = 0
        for i in range(-5, -1):
            if highs[i] < highs[i-1]:
                pullback_bars += 1
        if pullback_bars >= 2:
            # Check if most recent bar breaks above prior (High 1 or High 2)
            if highs[-1] > highs[-2] and is_bull_bar(-1):
                attempt_num = "High 2" if pullback_bars >= 3 else "High 1"
                conf = 75 if pullback_bars >= 3 else 60
                entry  = highs[-1] + 0.01
                stop   = lows[-2] - 0.01
                risk   = entry - stop
                target = entry + risk * 2
                signals.append({
                    'name'      : f"Brooks: {attempt_num} Pullback (Bull Trend Entry)",
                    'source'    : "Brooks Glossary / Ch.20",
                    'signal'    : '▲ BULL TREND PULLBACK',
                    'icon'      : '▲',
                    'color'     : '#27ae60',
                    'confidence': conf,
                    'value'     : f"20 EMA={ema20:.2f}  Pullback bars={pullback_bars}  Signal bar closes={closes[-1]:.2f}",
                    'entry'     : f"BUY STOP: {entry:.2f} (1 tick above {attempt_num} signal bar high)",
                    'stop'      : f"{stop:.2f} (below pullback swing low = {lows[-2]:.2f})",
                    'target'    : f"T1: Prior swing high  T2: {target:.2f} (2× risk)",
                    'desc'      : (
                        f"{attempt_num} pullback entry detected in bull trend.\n"
                        f"20 EMA = {ema20:.2f} (price above = bullish)\n"
                        f"Pullback duration: {pullback_bars} bars\n"
                        f"Signal bar: bull close at {closes[-1]:.2f}\n\n"
                        f"Brooks: {'High 2 = institutional backing. Both weak bulls AND weak bears shaken out.' if attempt_num == 'High 2' else 'High 1 = first attempt. Lower reliability — wait for High 2 if this fails.'}"
                    ),
                })

    # ── 5. MEASURED MOVE PROJECTION ────────────────────────────────────────
    if n >= 15:
        from scipy.signal import argrelextrema
        highs_idx = argrelextrema(df['High'].values, np.greater_equal, order=3)[0]
        lows_idx  = argrelextrema(df['Low'].values,  np.less_equal,    order=3)[0]

        if len(lows_idx) >= 2 and len(highs_idx) >= 1:
            l1_idx = lows_idx[-2]
            h1_idx = highs_idx[-1]
            l2_idx = lows_idx[-1]
            if l1_idx < h1_idx > l2_idx:
                leg1   = highs[h1_idx] - lows[l1_idx]
                corr   = (highs[h1_idx] - lows[l2_idx]) / highs[h1_idx] * 100
                if 25 <= corr <= 65 and leg1 > 0:
                    mm_target = lows[l2_idx] + leg1
                    risk = current - lows[l2_idx]
                    signals.append({
                        'name'      : "Brooks: Measured Move Projection",
                        'source'    : "Brooks Ch.20 / Ch.21",
                        'signal'    : '▲ MEASURED MOVE BULLISH',
                        'icon'      : '▲',
                        'color'     : '#3498db',
                        'confidence': 70,
                        'value'     : f"Leg1={leg1:.2f} pts  Correction={corr:.1f}%  Target={mm_target:.2f}",
                        'entry'     : f"BUY at correction low area: ~{lows[l2_idx]:.2f} (Leg 2 starting)",
                        'stop'      : f"{lows[l2_idx] * 0.99:.2f} (below correction low)",
                        'target'    : f"T1: {mm_target:.2f} (Leg 1 = {leg1:.2f} pts projected from correction low)  75% hit rate",
                        'desc'      : (
                            f"Measured Move detected.\n"
                            f"Leg 1: {lows[l1_idx]:.2f} → {highs[h1_idx]:.2f} = {leg1:.2f} pts\n"
                            f"Correction: {corr:.1f}% retracement (healthy: 25–65%)\n"
                            f"Correction low: {lows[l2_idx]:.2f}\n"
                            f"Target (Leg 1 = Leg 2): {mm_target:.2f}\n\n"
                            f"Brooks: 75% accuracy for achieving the equal-leg target.\n"
                            f"Use this as your primary target for with-trend trades."
                        ),
                    })

    # ── 6. TREND FROM THE OPEN (approximated from first N bars) ───────────
    if n >= 5:
        first5_bull = all(is_bull_bar(i) for i in range(min(5, n)))
        first5_bear = all(is_bear_bar(i) for i in range(min(5, n)))
        first5_sizes = [bar_size(i) for i in range(min(5, n))]
        all_large = all(s > avg_bar_size * 0.6 for s in first5_sizes)

        if (first5_bull or first5_bear) and all_large:
            direction = 'BULL' if first5_bull else 'BEAR'
            color = '#2ecc71' if first5_bull else '#e74c3c'
            icon  = '▲▲' if first5_bull else '▼▼'
            entry = f"Any with-trend pullback. Buy dips (bull) / sell rallies (bear). Every pullback is an entry."
            stop  = f"Below each pullback low (bull) / above each pullback high (bear)"
            tgt   = f"T1: 1× avg bar size from entry (scalp 50%). Hold 50% all day with trailing stop."
            signals.append({
                'name'      : f"Brooks: Trend from the Open ({direction})",
                'source'    : "Brooks Ch.23",
                'signal'    : f'{"▲▲ STRONG BULL" if direction=="BULL" else "▼▼ STRONG BEAR"} TREND DAY',
                'icon'      : icon,
                'color'     : color,
                'confidence': 80,
                'value'     : f"First {min(5,n)} bars all {direction.lower()} and large. Avg size={avg_bar_size:.2f}",
                'entry'     : entry,
                'stop'      : stop,
                'target'    : tgt,
                'desc'      : (
                    f"Trend from the Open — {direction} day detected.\n"
                    f"First {min(5,n)} bars all {direction.lower()} with strong bodies.\n"
                    f"Avg bar size = {avg_bar_size:.2f}\n\n"
                    f"Brooks: On this day type — trade ONLY with the trend.\n"
                    f"NO countertrend trades. Every pullback is an entry.\n"
                    f"Scalp 50%, swing 50%. The runner could be the best trade of the week."
                ),
            })

    # ── 7. WEDGE REVERSAL (Three pushes, each smaller) ─────────────────────
    # Detect 3 swing highs/lows where each push is progressively smaller
    if n >= 12:
        from scipy.signal import argrelextrema
        h_idx = argrelextrema(df['High'].values, np.greater_equal, order=3)[0]
        l_idx = argrelextrema(df['Low'].values,  np.less_equal,    order=3)[0]

        # Wedge TOP (3 swing highs, each smaller)
        if len(h_idx) >= 3:
            h1, h2, h3 = highs[h_idx[-3]], highs[h_idx[-2]], highs[h_idx[-1]]
            if h1 > h2 > h3 * 1.001:  # each push smaller (descending)
                diff1 = h1 - h2
                diff2 = h2 - h3
                if diff1 > 0 and diff2 > 0 and diff2 < diff1 * 1.5:
                    entry  = lows[-1] - 0.01
                    stop   = h3 + 0.01
                    risk   = stop - entry
                    target = entry - risk * 1.5
                    signals.append({
                        'name'      : "Brooks: Wedge Reversal (Bearish Top)",
                        'source'    : "Brooks Ch.14 / Ch.21",
                        'signal'    : '▼ THREE-PUSH EXHAUSTION TOP',
                        'icon'      : '▼',
                        'color'     : '#e74c3c',
                        'confidence': 70,
                        'value'     : f"Push1={h1:.2f}  Push2={h2:.2f}  Push3={h3:.2f}  Each smaller than prior",
                        'entry'     : f"SELL STOP: {entry:.2f} (1 tick below last bar low)",
                        'stop'      : f"{stop:.2f} (above 3rd push high = {h3:.2f})",
                        'target'    : f"T1: {lows[h_idx[-3]]:.2f} (start of wedge)  T2: {target:.2f}",
                        'desc'      : (
                            f"Wedge Top — Three diminishing pushes.\n"
                            f"Push 1 high: {h1:.2f}\n"
                            f"Push 2 high: {h2:.2f}\n"
                            f"Push 3 high: {h3:.2f}\n\n"
                            f"Brooks: Each push requires more effort but produces less.\n"
                            f"Structural exhaustion — bulls are losing power.\n"
                            f"Three trapped groups of buyers = your fuel on reversal."
                        ),
                    })

        # Wedge BOTTOM (3 swing lows, each smaller drop)
        if len(l_idx) >= 3:
            l1, l2, l3 = lows[l_idx[-3]], lows[l_idx[-2]], lows[l_idx[-1]]
            if l1 < l2 < l3 * 0.999:  # each push smaller (ascending lows)
                diff1 = l2 - l1
                diff2 = l3 - l2
                if diff1 > 0 and diff2 > 0 and diff2 < diff1 * 1.5:
                    entry  = highs[-1] + 0.01
                    stop   = l3 - 0.01
                    risk   = entry - stop
                    target = entry + risk * 1.5
                    signals.append({
                        'name'      : "Brooks: Wedge Reversal (Bullish Bottom)",
                        'source'    : "Brooks Ch.14 / Ch.21",
                        'signal'    : '▲ THREE-PUSH EXHAUSTION BOTTOM',
                        'icon'      : '▲',
                        'color'     : '#2ecc71',
                        'confidence': 70,
                        'value'     : f"Push1={l1:.2f}  Push2={l2:.2f}  Push3={l3:.2f}  Each shallower",
                        'entry'     : f"BUY STOP: {entry:.2f} (1 tick above last bar high)",
                        'stop'      : f"{stop:.2f} (below 3rd push low = {l3:.2f})",
                        'target'    : f"T1: {highs[l_idx[-3]]:.2f} (start of wedge)  T2: {target:.2f}",
                        'desc'      : (
                            f"Wedge Bottom — Three diminishing pushes down.\n"
                            f"Push 1 low: {l1:.2f}\n"
                            f"Push 2 low: {l2:.2f}\n"
                            f"Push 3 low: {l3:.2f}\n\n"
                            f"Brooks: Sellers losing power — each down push is shallower.\n"
                            f"Three trapped groups of sellers = buying fuel on reversal."
                        ),
                    })

    # ── 8. FAILED BREAKOUT (breakout then immediate reversal) ──────────────
    if n >= 5:
        from scipy.signal import argrelextrema
        h_idx = argrelextrema(df['High'].values, np.greater_equal, order=5)[0]
        l_idx = argrelextrema(df['Low'].values,  np.less_equal,    order=5)[0]

        # Bearish failed breakout: recent bar made new high but closed back below prior high
        if len(h_idx) >= 2:
            prior_high = highs[h_idx[-2]]
            # Did we break above prior high within last 3 bars and then reverse?
            for i in range(-4, -1):
                if highs[i] > prior_high and closes[i] < prior_high:
                    entry  = lows[-1] - 0.01
                    stop   = highs[i] + 0.01
                    risk   = stop - entry
                    target = entry - risk * 2
                    signals.append({
                        'name'      : "Brooks: Failed Breakout (Bearish)",
                        'source'    : "Brooks Ch.3 / Ch.12",
                        'signal'    : '▼ FAILED BULL BREAKOUT',
                        'icon'      : '▼',
                        'color'     : '#e74c3c',
                        'confidence': 73,
                        'value'     : f"Prior high={prior_high:.2f}  Bar broke to {highs[i]:.2f} then closed at {closes[i]:.2f}",
                        'entry'     : f"SELL STOP: {entry:.2f} (1 tick below signal bar low)",
                        'stop'      : f"{stop:.2f} (above failed breakout bar high = {highs[i]:.2f})",
                        'target'    : f"T1: Opposite range extreme  T2: {target:.2f} (2× risk)",
                        'desc'      : (
                            f"Failed Breakout (Bearish) detected.\n"
                            f"Prior swing high = {prior_high:.2f}\n"
                            f"Breakout bar reached: {highs[i]:.2f}\n"
                            f"But closed back at: {closes[i]:.2f} (below the level)\n\n"
                            f"Brooks: 'Most breakouts fail.' Trapped bulls from\n"
                            f"the breakout bar are now your fuel. Their stop-loss\n"
                            f"sells = your profit as price falls."
                        ),
                    })
                    break

        # Bullish failed breakout: broke below prior low but reversed back above it
        if len(l_idx) >= 2:
            prior_low = lows[l_idx[-2]]
            for i in range(-4, -1):
                if lows[i] < prior_low and closes[i] > prior_low:
                    entry  = highs[-1] + 0.01
                    stop   = lows[i] - 0.01
                    risk   = entry - stop
                    target = entry + risk * 2
                    signals.append({
                        'name'      : "Brooks: Failed Breakout (Bullish)",
                        'source'    : "Brooks Ch.3 / Ch.12",
                        'signal'    : '▲ FAILED BEAR BREAKOUT',
                        'icon'      : '▲',
                        'color'     : '#2ecc71',
                        'confidence': 73,
                        'value'     : f"Prior low={prior_low:.2f}  Bar broke to {lows[i]:.2f} then closed at {closes[i]:.2f}",
                        'entry'     : f"BUY STOP: {entry:.2f} (1 tick above signal bar high)",
                        'stop'      : f"{stop:.2f} (below failed breakout low = {lows[i]:.2f})",
                        'target'    : f"T1: Opposite range extreme  T2: {target:.2f} (2× risk)",
                        'desc'      : (
                            f"Failed Breakout (Bullish) detected.\n"
                            f"Prior swing low = {prior_low:.2f}\n"
                            f"Breakdown bar reached: {lows[i]:.2f}\n"
                            f"But closed back at: {closes[i]:.2f} (above the level)\n\n"
                            f"Brooks: Trapped bears from the breakdown are your fuel.\n"
                            f"Their covering = your profit as price rises."
                        ),
                    })
                    break

    # ── 9. BREAKOUT PULLBACK ────────────────────────────────────────────────
    # Recent breakout above swing high followed by a tight 2-5 bar pullback
    if n >= 10:
        from scipy.signal import argrelextrema
        h_idx = argrelextrema(df['High'].values, np.greater_equal, order=4)[0]
        if len(h_idx) >= 2:
            prior_swing_high = highs[h_idx[-2]]
            breakout_bar_idx = h_idx[-1]
            # Was there a breakout above the prior swing high?
            if (highs[breakout_bar_idx] > prior_swing_high and
                    closes[breakout_bar_idx] > prior_swing_high and
                    n - breakout_bar_idx <= 6):
                # Check pullback: bars after breakout are smaller and holding
                pullback_bars = n - breakout_bar_idx - 1
                if 1 <= pullback_bars <= 5:
                    pb_lows  = [lows[breakout_bar_idx + j] for j in range(1, pullback_bars + 1)]
                    pb_sizes = [bar_size(breakout_bar_idx + j) for j in range(1, pullback_bars + 1)]
                    avg_pb   = np.mean(pb_sizes) if pb_sizes else avg_bar_size
                    tight    = avg_pb < avg_bar_size * 1.2
                    holds    = min(pb_lows) > prior_swing_high * 0.997  # above breakout level

                    if tight and holds:
                        entry  = highs[-1] + 0.01
                        stop   = min(pb_lows) - 0.01
                        risk   = entry - stop
                        bk_ht  = closes[breakout_bar_idx] - lows[breakout_bar_idx]
                        target = entry + bk_ht * 2
                        signals.append({
                            'name'      : "Brooks: Breakout Pullback (Long)",
                            'source'    : "Brooks Ch.3 / Ch.12",
                            'signal'    : '▲ BREAKOUT PULLBACK LONG',
                            'icon'      : '▲',
                            'color'     : '#27ae60',
                            'confidence': 80,
                            'value'     : f"Broke {prior_swing_high:.2f}  Pullback {pullback_bars} bars  Holding above breakout",
                            'entry'     : f"BUY STOP: {entry:.2f} (1 tick above signal bar high)",
                            'stop'      : f"{stop:.2f} (1 tick below pullback low = {min(pb_lows):.2f})",
                            'target'    : f"T1: {entry + bk_ht:.2f} (breakout bar height)  T2: {target:.2f} (×2)",
                            'desc'      : (
                                f"Breakout Pullback detected.\n"
                                f"Prior swing high: {prior_swing_high:.2f}\n"
                                f"Breakout bar: {highs[breakout_bar_idx]:.2f}\n"
                                f"Pullback: {pullback_bars} bars, tight, holding above breakout level\n\n"
                                f"Brooks: Highest-probability setup.\n"
                                f"Two proofs: (1) strong enough to break the level,\n"
                                f"(2) level held on retest = genuine breakout."
                            ),
                        })

    # ── 10. SPIKE AND CHANNEL ───────────────────────────────────────────────
    # Detect: a fast spike (2+ large same-direction bars) followed by channel
    if n >= 15:
        spike_len = 0
        spike_dir = None
        for i in range(-8, -1):
            if is_bull_bar(i) and is_strong_bar(i, 0.6) and bar_size(i) > avg_bar_size:
                if spike_dir is None or spike_dir == 'bull':
                    spike_dir = 'bull'
                    spike_len += 1
            elif is_bear_bar(i) and is_strong_bar(i, 0.6) and bar_size(i) > avg_bar_size:
                if spike_dir is None or spike_dir == 'bear':
                    spike_dir = 'bear'
                    spike_len += 1
            else:
                if spike_len >= 2:
                    break
                spike_len = 0
                spike_dir = None

        if spike_len >= 2 and spike_dir:
            # Check if recent bars show channel (overlapping, smaller)
            channel_bars = []
            for i in range(-4, 0):
                if bar_size(i) < avg_bar_size * 1.1:
                    channel_bars.append(i)

            if len(channel_bars) >= 2:
                col   = '#2ecc71' if spike_dir == 'bull' else '#e74c3c'
                icon  = '▲' if spike_dir == 'bull' else '▼'
                sig_  = f'{"▲ BULL" if spike_dir=="bull" else "▼ BEAR"} SPIKE AND CHANNEL'
                entry_txt = (
                    f"BUY pullback to channel line (bull) / SELL rally to channel line (bear)"
                )
                stop_txt = f"Below signal bar low in channel"
                tgt_txt  = f"T1: Prior channel swing extreme  T2: Measured move = spike height from channel start"
                signals.append({
                    'name'      : f"Brooks: Spike and Channel ({'Bull' if spike_dir=='bull' else 'Bear'})",
                    'source'    : "Brooks Ch.21",
                    'signal'    : sig_,
                    'icon'      : icon,
                    'color'     : col,
                    'confidence': 68,
                    'value'     : f"Spike length: {spike_len} strong bars  Direction: {spike_dir.upper()}  Channel bars: {len(channel_bars)}",
                    'entry'     : entry_txt,
                    'stop'      : stop_txt,
                    'target'    : tgt_txt,
                    'desc'      : (
                        f"Spike and Channel detected.\n"
                        f"Spike: {spike_len} strong {spike_dir} bars\n"
                        f"Channel phase: {len(channel_bars)} smaller overlapping bars\n\n"
                        f"Brooks: The master trend pattern. During the channel,\n"
                        f"ONLY trade with-trend pullbacks to the channel line.\n"
                        f"Do NOT scalp countertrend — most costly mistake in trading."
                    ),
                })

    # ── 11. TREND LINE BREAK AND LOWER HIGH ────────────────────────────────
    # Detect: price dropped below a recent trend line, then made a lower high
    if n >= 20:
        from scipy.signal import argrelextrema
        h_idx = argrelextrema(df['High'].values, np.greater_equal, order=4)[0]
        l_idx = argrelextrema(df['Low'].values,  np.less_equal,    order=4)[0]

        if len(h_idx) >= 3 and len(l_idx) >= 2:
            # Simple trend line: connect last two swing lows
            sl1_idx, sl2_idx = l_idx[-2], l_idx[-1]
            sl1_val, sl2_val = lows[sl1_idx], lows[sl2_idx]

            if sl2_idx > sl1_idx and sl2_val > sl1_val:  # rising swing lows = uptrend
                # Project trend line to current bar
                slope = (sl2_val - sl1_val) / (sl2_idx - sl1_idx)
                tl_current = sl2_val + slope * (n - 1 - sl2_idx)

                # Has price broken below the trend line?
                tl_broken = closes[-1] < tl_current

                if tl_broken:
                    # Is the most recent swing high lower than the one before?
                    if len(h_idx) >= 2:
                        last_h  = highs[h_idx[-1]]
                        prior_h = highs[h_idx[-2]]
                        lower_high = last_h < prior_h

                        if lower_high:
                            entry  = lows[-1] - 0.01
                            stop   = last_h + 0.01
                            risk   = stop - entry
                            target = entry - (prior_h - last_h) * 2
                            signals.append({
                                'name'      : "Brooks: Trend Line Break + Lower High",
                                'source'    : "Brooks Ch.13",
                                'signal'    : '▼ MAJOR REVERSAL SIGNAL',
                                'icon'      : '▼▼',
                                'color'     : '#c0392b',
                                'confidence': 75,
                                'value'     : f"TL broken: price {closes[-1]:.2f} < TL {tl_current:.2f}  Lower high: {last_h:.2f} < {prior_h:.2f}",
                                'entry'     : f"SELL STOP: {entry:.2f} (below signal bar at lower high)",
                                'stop'      : f"{stop:.2f} (above lower high = {last_h:.2f})",
                                'target'    : f"T1: {lows[l_idx[-1]]:.2f} (TL break swing low)  T2: {target:.2f}",
                                'desc'      : (
                                    f"Trend Line Break + Lower High — Major Reversal.\n"
                                    f"Step 1 ✅: Trend line broken (price {closes[-1]:.2f} < TL {tl_current:.2f})\n"
                                    f"Step 2 ✅: Lower high formed ({last_h:.2f} < {prior_h:.2f})\n\n"
                                    f"Brooks: Both conditions confirmed = highest-reliability reversal.\n"
                                    f"The lower high IS the short entry with a defined stop.\n"
                                    f"Expect minimum two legs down after this signal."
                                ),
                            })

    # ── 12. FINAL FLAG ──────────────────────────────────────────────────────
    # A prolonged trend followed by a tight range (small overlapping bars) near the extreme
    if n >= 20:
        # Check for prolonged trend: price well above/below EMA for many bars
        above_ema_count = sum(1 for i in range(-15, -5) if closes[i] > ema20_series.iloc[i])
        below_ema_count = sum(1 for i in range(-15, -5) if closes[i] < ema20_series.iloc[i])

        # Recent bars: tight range (small bodies, overlapping)
        recent_sizes = [bar_size(i) for i in range(-6, 0)]
        tight_recent = all(s < avg_bar_size * 0.8 for s in recent_sizes)
        recent_high  = max(highs[i] for i in range(-6, 0))
        recent_low   = min(lows[i]  for i in range(-6, 0))
        flag_range   = recent_high - recent_low

        # Final flag top (prolonged bull, tight range at top)
        if above_ema_count >= 8 and tight_recent:
            # Check if breakout of this range failed (bar broke above but closed inside)
            failed = False
            for i in range(-4, 0):
                if highs[i] > recent_high * 1.001 and closes[i] < recent_high:
                    failed = True
                    break

            if failed:
                entry  = recent_low - 0.01
                stop   = recent_high + 0.01
                risk   = stop - entry
                target = entry - flag_range * 3
                signals.append({
                    'name'      : "Brooks: Final Flag (Bearish Reversal)",
                    'source'    : "Brooks Ch.21 / Ch.16",
                    'signal'    : '▼ FINAL FLAG — MAJOR TOP',
                    'icon'      : '▼▼',
                    'color'     : '#c0392b',
                    'confidence': 72,
                    'value'     : f"Prolonged bull ({above_ema_count} bars above EMA)  Tight flag: {recent_low:.2f}–{recent_high:.2f}  Failed breakout detected",
                    'entry'     : f"SELL STOP: {entry:.2f} (below flag low after failed breakout)",
                    'stop'      : f"{stop:.2f} (above failed breakout high = {recent_high:.2f})",
                    'target'    : f"T1: Start of final leg up  T2: {target:.2f} (flag range × 3)",
                    'desc'      : (
                        f"Final Flag (Bearish) detected.\n"
                        f"Prolonged bull trend: {above_ema_count} bars above EMA\n"
                        f"Tight flag range: {recent_low:.2f} – {recent_high:.2f}\n"
                        f"Failed breakout above flag: ✅ confirmed\n\n"
                        f"Brooks: The most dangerous trap in trend trading.\n"
                        f"Looks like a safe continuation — it is NOT.\n"
                        f"All the late buyers are now your fuel for the reversal."
                    ),
                })

    # Sort by confidence
    signals.sort(key=lambda x: x['confidence'], reverse=True)
    return signals



# ─────────────────────────────────────────────────────────────────────────────
#  STREET SMARTS ENGINE
#  Source: Street Smarts — Linda Bradford Raschke & Laurence A. Connors (1996)
#  All signals computed purely from OHLC data
# ─────────────────────────────────────────────────────────────────────────────

STREET_SMARTS_DB = {

    "Turtle Soup": {
        "source": "Raschke & Connors Ch.1",
        "type": "test", "direction": "reversal",
        "rating": "★★★★★ Still works 2025",
        "concept": (
            "The Turtle system buys 20-day highs and sells 20-day lows. Most of "
            "these breakouts are false. Turtle Soup fades them — entering a reversal "
            "as trapped Turtle traders are squeezed out. When a 20-day extreme is "
            "made and immediately reverses, those breakout buyers/sellers are trapped "
            "and their forced exit is your fuel. Modern equivalent: ICT's Liquidity Raid."
        ),
        "pre_market": [
            "Scan for markets at or near 20-day highs or lows the evening before",
            "Previous 20-day extreme must be AT LEAST 4 trading sessions old — critical filter",
            "No major scheduled news event on entry day",
            "2025: check if the 20-day extreme aligns with a daily Order Block for confluence",
        ],
        "trading_plan": {
            "entry": "Buy stop 5–10 ticks ABOVE the prior 20-day low (after today makes new 20-day low). Good for today only.",
            "stop":  "1 tick below today's new low — placed immediately on fill",
            "target_1": "Prior swing high in the vicinity — scale 50%",
            "target_2": "Trail stop below each new swing high as position matures",
            "manage": "Parabolic range-expansion bar = exit all immediately. Do not carry losing positions overnight.",
            "avoid": "Prior 20-day extreme less than 4 sessions old. Strong ADX>45 uptrend — skip the fade.",
        },
        "review_2025": "Works because stop orders always cluster at 20-day extremes — structural feature of all markets. ICT, Brooks, and Wyckoff all independently identify this same setup.",
    },

    "Turtle Soup Plus One": {
        "source": "Raschke & Connors Ch.1",
        "type": "test", "direction": "reversal",
        "rating": "★★★★★ Still works 2025",
        "concept": (
            "Same logic as Turtle Soup but entry is the NEXT day. Day 1: new 20-day "
            "extreme made AND close is at or beyond the prior extreme (trapping "
            "close-on-breakout players too). Day 2: stop triggers as price reverses. "
            "More participants are trapped = larger forced-exit move."
        ),
        "pre_market": [
            "Evening before: identify market that made new 20-day high/low AND closed at or beyond prior 20-day extreme",
            "Prior 20-day extreme must be at least 3 trading sessions old",
            "Advantage: you know the setup the evening before — place resting stop next morning",
            "Best candidates: markets with wide daily range and active volume",
        ],
        "trading_plan": {
            "entry": "Resting buy stop at the prior 20-day low level — placed next morning. Valid Day 2 only.",
            "stop":  "1 tick below the LOWER of Day 1 low or Day 2 low",
            "target_1": "Prior swing high 2–3 sessions back — scale 50% within first 6 bars",
            "target_2": "Trail stop on remaining position below each new higher low",
            "manage": "Strong close on Day 2 = carry overnight. Trade closes flat or down Day 2 = exit at close.",
            "avoid": "ADX > 45 and steeply rising = genuine trend, not a false breakout. Skip.",
        },
        "review_2025": "Easier to monitor than Turtle Soup (know setup the night before). The double squeeze — Day 1 AND Day 2 breakout buyers both trapped — makes the reversal more powerful.",
    },

    "80-20s": {
        "source": "Raschke & Connors Ch.3",
        "type": "test", "direction": "reversal",
        "rating": "★★★★☆ Works well adapted",
        "concept": (
            "If the prior day opened in the top 20% of its range AND closed in the "
            "bottom 20% (or vice versa), a reversal setup exists for the next day. "
            "Today the market probes beyond yesterday's extreme, then reverses back "
            "through it. Same as ICT's Power of 3 — the Judas Swing creates a false "
            "move before the real direction begins."
        ),
        "pre_market": [
            "Evening scan: Yesterday opened in top 20% of range AND closed in bottom 20% = sell setup",
            "OR: Yesterday opened in bottom 20% AND closed in top 80% = buy setup",
            "Use day-session data only — ignore overnight/globex for range calculation",
            "2025 filter: check if yesterday's close is near a PDH/PDL for additional confluence",
        ],
        "trading_plan": {
            "entry": "Buy stop at yesterday's HIGH (for buy setup) — triggered only if today trades ≥5 ticks above/below yesterday's extreme first.",
            "stop":  "1 tick above today's high (shorts) or below today's low (longs)",
            "target_1": "Previous day's low (for buy) — day trade only, scale 50%",
            "target_2": "Trail to capture move — exit before last 30 min",
            "manage": "Day trade ONLY — exit all positions by 3:30 PM EST. No overnight holds.",
            "avoid": "ADX > 35 and steeply rising trending days — the 80-20 bar may be a continuation flag.",
        },
        "review_2025": "The morning false move (Judas Swing) is as predictable as ever. The key filter: ADX must not be extremely high and rising. In neutral/choppy markets this is consistently reliable.",
    },

    "Momentum Pinball": {
        "source": "Raschke & Connors Ch.4",
        "type": "test", "direction": "mean_reversion",
        "rating": "★★★★☆ High consistency",
        "concept": (
            "Calculate RSI(3) of the daily net change (today's close minus yesterday's close). "
            "When this drops below 30 (Day 1), the market has sold off too much in 2–3 days. "
            "Enter long on Day 2 by breaking above the first hour's range high. Exploits "
            "the statistical tendency for 2–3 day mean reversion in all markets."
        ),
        "pre_market": [
            "Evening: compute RSI(3) of daily net change series. If < 30: buy setup. If > 70: sell setup.",
            "Modern replacement: RSI(2) of daily Close — if RSI(2) < 10: buy. If RSI(2) > 90: sell.",
            "Not appropriate in strongly trending markets (ADX > 30 and rising)",
            "Note the first hour's high and low before market opens next morning",
        ],
        "trading_plan": {
            "entry": "Buy stop ABOVE the first hour's trading range high (9:30–10:30 AM). If not triggered by 11 AM: no trade.",
            "stop":  "At the first hour's LOW — placed immediately on fill",
            "target_1": "Day 2 target: close with a profit — carry overnight if profitable",
            "target_2": "Day 3 exit: morning follow-through — exit near open or prior day's high",
            "manage": "Trade closes profitably Day 2 = carry overnight. Trade closes flat/down Day 2 = exit at close. Hold max 3 days.",
            "avoid": "Strong trending markets (ADX > 30 rising) — overbought/oversold can persist for days.",
        },
        "review_2025": "The first-hour range breakout filter is the key insight — you enter only when market confirms movement in your direction. RSI(2) version is the modernized update Connors himself published later.",
    },

    "The Anti": {
        "source": "Raschke & Connors Ch.5",
        "type": "retracement", "direction": "with-trend",
        "rating": "★★★★★ Excellent — very reliable",
        "concept": (
            "The slow %D stochastic defines the trend (momentum trend). The fast %K "
            "represents short-term oscillations within that trend. When %D trends up "
            "and %K pulls back toward %D then hooks back up — this is the Anti buy. "
            "Two timeframes of momentum aligning creates positive feedback = explosive moves."
        ),
        "pre_market": [
            "Stochastic parameters: %K = 7-period, %D = 10-period slow",
            "%D must have a definite sustained upward slope (for buy setups) — not just 1-day uptick",
            "%K must have pulled back toward %D for at least 2–3 bars",
            "Draw a downtrend line across tops of the price consolidation — breakout is your trigger",
            "Avoid: ADX < 16 (too quiet) or ADX > 45 (too strong — Anti may not work)",
        ],
        "trading_plan": {
            "entry": "Buy stop 1 tick above prior bar's high when %K hooks back up toward %D. OR breakout of price consolidation trendline.",
            "stop":  "Just below the entry bar low. OR below the most recent swing low during the %K pullback.",
            "target_1": "Range expansion bar within 3–4 bars = exit entire position (that IS the climax)",
            "target_2": "Hold max 4 bars/days regardless — time objective achieved",
            "manage": "Trail stop below each successive higher low once in profit. Market stalls 3+ bars with no progress: exit — move didn't materialize.",
            "avoid": "Very quiet low-ADX markets. At major resistance/support levels where the trend may simply be running into a wall.",
        },
        "review_2025": "Linda has traded this for 30+ years with consistent results on every timeframe from 5-min to weekly. The stochastic hook is an elegant way to identify when a short-term correction is ending within a longer momentum trend.",
    },

    "The Holy Grail (LBR)": {
        "source": "Raschke & Connors Ch.6",
        "type": "retracement", "direction": "with-trend",
        "rating": "★★★★★ Most reliable in book",
        "concept": (
            "In a strongly trending market (ADX > 30 and rising), the 20-period EMA "
            "acts as perfect support/resistance during pullbacks. ADX turning down "
            "during the pullback does NOT mean trend reversal — it means consolidation. "
            "When price touches the 20 EMA during the ADX pullback: low-risk re-entry "
            "into the continuation of the trend."
        ),
        "pre_market": [
            "14-period ADX must be > 30 AND rising — genuine trending market confirmed",
            "Watch for first pullback in price toward the 20-period EMA",
            "ADX turns down or levels during pullback — this is NORMAL, not a reversal signal",
            "After success: ADX must turn up above 30 again before next 20 EMA touch can be traded",
        ],
        "trading_plan": {
            "entry": "Buy stop 1 tick above prior bar's high when price is AT the 20 EMA. 2025: also look for an Order Block or FVG at the EMA.",
            "stop":  "At the newly formed swing low (the pullback low)",
            "target_1": "Most recent swing high — scale 40–50%, move stop to breakeven",
            "target_2": "If ADX continues rising: hold for new trend leg — trail with swing lows",
            "manage": "ADX turns back up strongly after pullback: hold aggressively — large leg may follow. Re-entry rule: if stopped out, re-enter at original entry price (once).",
            "avoid": "Do not exit longs just because ADX ticks down — this is the most common mistake. ADX turning down is consolidation, not reversal.",
        },
        "review_2025": "Three independent frameworks identify this exact setup: Raschke (Holy Grail), Carter (Holy Grail), ICT (OTE pullback to Order Block). When three successful traders 25 years apart arrive at the same setup — it is structural, not coincidence.",
    },

    "ADX Gapper": {
        "source": "Raschke & Connors Ch.7",
        "type": "retracement", "direction": "with-trend",
        "rating": "★★★★☆ Very good with filter",
        "concept": (
            "In a strongly trending market, gaps against the trend are short-lived — "
            "the trend absorbs them. Wait for a gap against the prevailing trend "
            "(confirmed by ADX + DI lines), then enter when the market reverses back "
            "into trend direction. Institutions use the gap to accumulate at better "
            "prices before the trend resumes."
        ),
        "pre_market": [
            "12-period ADX > 30 — strong trend in effect",
            "+DI > -DI confirms uptrend (for buy setups)",
            "Today's open must gap below yesterday's low (for bull trend fade)",
            "Place buy stop at yesterday's low — set before market opens",
            "Skip on major scheduled news days (NFP, Fed, CPI)",
        ],
        "trading_plan": {
            "entry": "Buy stop in the area of yesterday's low (gap-down day, bull trend). Must gap below yesterday's low at open — if no gap, no trade.",
            "stop":  "1 tick below today's morning low (the gap-down extreme)",
            "target_1": "Yesterday's close or high — scale 50%",
            "target_2": "Trail into the close — hold overnight if closes strongly (top 25% of range)",
            "manage": "Strong close = carry overnight for next morning follow-through. Weak close = exit before close. Parabolic move: exit all immediately.",
            "avoid": "News-driven gaps — an unexpected shock can gap that does not reverse. Skip on heavy news days.",
        },
        "review_2025": "The ADX filter transforms a mediocre gap-fade into a high-quality setup. Without ADX, gap reversal trades have ~50% accuracy. With ADX > 30 the win rate increases substantially.",
    },

    "Whiplash": {
        "source": "Raschke & Connors Ch.8",
        "type": "climax", "direction": "reversal",
        "rating": "★★★★☆ Simple, reliable",
        "concept": (
            "The market gaps lower AND reverses during the day to close above the "
            "opening and in the upper half of the range. This two-directional action "
            "signals the gap was an overreaction. Enter Market-On-Close exploiting "
            "the statistical follow-through tendency next morning."
        ),
        "pre_market": [
            "Today must have gapped lower than yesterday's low at the open",
            "Monitor throughout the day: close must be above the opening price",
            "AND close must be in the top 50% of today's range",
            "Both conditions must be met by close — only then place MOC order",
        ],
        "trading_plan": {
            "entry": "Buy MOC (Market-On-Close) — entered at the close of the setup day. Do not enter unless BOTH conditions confirmed.",
            "stop":  "If next morning opens BELOW today's close: EXIT IMMEDIATELY at the open. A bad open = your stop.",
            "target_1": "Morning follow-through — exit in first 15–30 minutes of next session",
            "target_2": "If market gaps open strongly: exit immediately — the gap IS the target",
            "manage": "Good open next morning: trail a tight stop immediately. Gap open in your favor: exit at-market ('When the ducks quack, feed them').",
            "avoid": "Individual stocks with thin liquidity at close. Prefer futures (ES, NQ) or liquid ETFs for MOC entries.",
        },
        "review_2025": "The MOC entry is elegant — entering after the market has already proven the reversal. ~60% win rate confirmed. Works especially well in actively traded index futures.",
    },

    "Three-Day Unfilled Gap": {
        "source": "Raschke & Connors Ch.9",
        "type": "climax", "direction": "reversal",
        "rating": "★★★★☆ High reward potential",
        "concept": (
            "A gap that is not filled for 3 days represents a significant supply/demand "
            "imbalance. When the market finally begins to close this gap, momentum picks "
            "up rapidly. Similar to an island reversal — isolated unfilled gaps from "
            "extremes often signal the start of significant counter-moves."
        ),
        "pre_market": [
            "Today the market gaps lower and does NOT fill the gap during the day session",
            "Place buy stop 1 tick above the HIGH of the gap-down day — valid for 3 trading sessions",
            "If not triggered within 3 sessions: cancel the order entirely",
            "Best candidates: volatile instruments with above-average gap-day volume",
        ],
        "trading_plan": {
            "entry": "Resting buy stop 1 tick above gap-day high — valid for 3 days only. Entry trigger = market begins closing the gap.",
            "stop":  "1 tick below the gap-day LOW",
            "target_1": "Pre-gap level / prior support before the gap occurred — scale 50%",
            "target_2": "Once gap fully closed: watch for reversal signals — may resume original direction",
            "manage": "Once gap starts closing momentum often accelerates — move stop quickly. Works especially well in volatile stocks and commodities.",
            "avoid": "Low-volume gaps on thin news. High-volume climactic gaps are the best candidates. 2025: ignore overnight/extended hours gaps — use day-session data only.",
        },
        "review_2025": "Unfilled gaps are magnetic — price is 'owed' trades at those levels. When the gap closes, momentum typically accompanies the move. Add filter: gap-day volume above average.",
    },

    "Picture Patterns (Library)": {
        "source": "Raschke & Connors Ch.10",
        "type": "climax", "direction": "both",
        "rating": "★★★★★ Requires experience — cannot be auto-detected",
        "concept": (
            "Three visual patterns that occur at exhaustion points: "
            "(1) Spike & Ledge: sharp spike followed by tight consolidation (the ledge). "
            "(2) Three Little Indians: three symmetrical peaks/troughs. "
            "(3) Fakeout-Shakeout: breakout from a range that immediately reverses. "
            "Common thread: all three have a definite risk point and reward almost immediately."
        ),
        "pre_market": [
            "These require real-time chart monitoring — cannot be scanned pre-market",
            "Look for: (1) a sharp climactic spike, (2) three symmetrical pivots, (3) a breakout that reverses within 1–5 bars",
            "The risk point must be visible BEFORE you enter — locate it first",
            "Winning trades from these patterns 'do not look back' — that is the defining characteristic",
        ],
        "trading_plan": {
            "entry": "Spike & Ledge: stop on breakdown of ledge. Three Indians: at-market on third peak reversal. Fakeout: stop above congestion midpoint.",
            "stop":  "Spike & Ledge: opposite side of ledge. Three Indians: above/below third peak. Fakeout: below the trap low.",
            "target_1": "Range expansion bar = exit immediately at-market",
            "target_2": "Trail stop below each new swing in your direction",
            "manage": "Move stop to breakeven immediately on any profit. If trade does not reward almost immediately: something is wrong — exit.",
            "avoid": "These require tape reading — minimum 6 months of daily chart review before trading live.",
        },
        "review_2025": "Spike & Ledge = ICT Order Block after a spike. Three Indians = Brooks Wedge Reversal. Fakeout-Shakeout = Brooks Failed Failure. The mechanics are unchanged across all eras.",
    },

    "Wolfe Wave (Library)": {
        "source": "Raschke & Connors Ch.11",
        "type": "projection", "direction": "both",
        "rating": "★★★★☆ Unique — cannot be reliably auto-detected",
        "concept": (
            "Based on Newton's law: for every action an equal and opposite reaction. "
            "Five-point wave structure where points 1, 3, and 5 form a trendline "
            "projecting to a price target (EPA — Estimated Price at Arrival). Enter "
            "at point 5, target the EPA line (drawn from points 1 to 4). Surprisingly accurate."
        ),
        "pre_market": [
            "Point 2: begin counting here — a significant swing high",
            "Point 3: low of first decline from point 2",
            "Point 1: low BEFORE point 2 — must be LOWER than point 3",
            "Point 4: high of rally from point 3 — must be HIGHER than point 1",
            "Trendline 1-3 projected forward = where point 5 will form (entry zone)",
            "Trendline 1-4 = EPA target line",
        ],
        "trading_plan": {
            "entry": "At-market when price reaches the 1-3 trendline extension (point 5) AND shows first signs of reversal.",
            "stop":  "Just below the newly formed reversal at point 5",
            "target_1": "EPA line (trendline from point 1 to point 4 extended) — moving target, changes daily",
            "target_2": "Trail stop below each successive swing as position matures",
            "manage": "Move to breakeven immediately on any profit. Good trades 'do not look back'. If EPA is approached: tighten stop and prepare to exit.",
            "avoid": "This is the most subjective setup in the book. Do not trade live until you've spent months identifying waves on historical charts. Use as a TARGET TOOL for existing positions first.",
        },
        "review_2025": "The EPA projection mechanism is one of the most elegant in technical analysis. Worth learning as a TARGET tool even if you don't use it for entries. Found 3–6 times per week on 5-min S&P charts.",
    },

    "News Reversal": {
        "source": "Raschke & Connors Ch.12",
        "type": "climax", "direction": "both",
        "rating": "★★★★★ One of the best setups ever",
        "concept": (
            "When an 8:30 AM economic report is released and the market spikes 4+ ticks "
            "in the 'logical' direction, then immediately reverses back through the prior "
            "day's high/low — the market is talking: the news is already priced in. "
            "Fade the spike, trade the reversal. The initial reaction is emotion; the "
            "second reaction is where real money decides."
        ),
        "pre_market": [
            "Mark yesterday's high and low for your market before the 8:30 EST release",
            "Know which economic report is being released (NFP, CPI, GDP, Retail Sales)",
            "Have a sell stop 1–3 ticks BELOW yesterday's high (for bull spike fade)",
            "Have a buy stop 1–3 ticks ABOVE yesterday's low (for bear spike fade)",
            "Requires fast execution — the reversal can happen within minutes of 8:30 EST",
        ],
        "trading_plan": {
            "entry": "Sell stop 1–3 ticks BELOW yesterday's high — triggered as price reverses back below it (after spiking 4+ ticks above). OR buy stop above yesterday's low (after spike down).",
            "stop":  "1 tick above today's high (the spike extreme) for shorts. Move to breakeven immediately on profit.",
            "target_1": "First major support/resistance below entry — scale 50–100%",
            "target_2": "Trail a trailing stop — these moves can last 30 min to several hours",
            "manage": "Parabolic drop within first 30 minutes: exit all. If market consolidates after initial reversal: the move is continuing — hold.",
            "avoid": "If the initial 'logical' direction move does NOT reverse within 5–10 minutes: cancel the fade. The news was a genuine surprise. Also avoid extreme volatility events (market crashes).",
        },
        "review_2025": "Works the same in 2025 on NFP, CPI, Fed announcements. The first reaction is driven by algorithms and panic, not by understanding. The second reaction = real money deciding. This is the definition of 'listening to the market'.",
    },
}


def _rsi(series, period):
    """Compute RSI of a pandas Series."""
    delta = series.diff()
    gain  = delta.clip(lower=0).rolling(period, min_periods=1).mean()
    loss  = (-delta.clip(upper=0)).rolling(period, min_periods=1).mean()
    rs    = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def _stoch(high, low, close, k_period=7, d_period=10):
    """Compute %K and %D stochastics."""
    lowest  = low.rolling(k_period,  min_periods=1).min()
    highest = high.rolling(k_period, min_periods=1).max()
    rng     = (highest - lowest).replace(0, np.nan)
    pct_k   = (close - lowest) / rng * 100
    pct_d   = pct_k.rolling(d_period, min_periods=1).mean()
    return pct_k, pct_d


def _adx(high, low, close, period=14):
    """Compute ADX, +DI, -DI."""
    tr1  = high - low
    tr2  = (high - close.shift()).abs()
    tr3  = (low  - close.shift()).abs()
    tr   = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr  = tr.rolling(period, min_periods=1).mean()

    up   = high.diff()
    down = -low.diff()
    pdm  = up.where((up > down) & (up > 0), 0.0)
    ndm  = down.where((down > up) & (down > 0), 0.0)

    pdi  = pdm.rolling(period, min_periods=1).mean() / atr.replace(0, np.nan) * 100
    ndi  = ndm.rolling(period, min_periods=1).mean() / atr.replace(0, np.nan) * 100
    dx   = ((pdi - ndi).abs() / (pdi + ndi).replace(0, np.nan) * 100)
    adx  = dx.rolling(period, min_periods=1).mean()
    return adx, pdi, ndi


def detect_street_smarts(df):
    """
    Detect Street Smarts signals from OHLC data.
    All computed purely from OHLC bars.
    Returns list of signal dicts.
    """
    signals = []
    n = len(df)
    if n < 22:
        return signals

    closes = df['Close'].values
    highs  = df['High'].values
    lows   = df['Low'].values
    opens  = df['Open'].values
    curr   = closes[-1]

    # ── 1. TURTLE SOUP ────────────────────────────────────────────────────
    # Today made new 20-day low AND prior 20-day low is ≥4 sessions old
    roll_period = min(20, n - 1)
    roll_high   = df['High'].rolling(roll_period).max()
    roll_low    = df['Low'].rolling(roll_period).min()

    today_20d_low  = roll_low.iloc[-1]
    today_20d_high = roll_high.iloc[-1]

    # Find when the prior 20-day extreme was set
    def days_since_extreme(series, is_min=True):
        vals = series.values
        ext  = vals[-1]
        for j in range(2, min(n, 30)):
            if is_min and vals[-j] < ext * 0.9999:
                return j - 1
            if not is_min and vals[-j] > ext * 1.0001:
                return j - 1
        return 30

    # Turtle Soup LONG (new 20-day low, prior extreme ≥4 days ago)
    if lows[-1] <= today_20d_low * 1.001:  # made new or near 20-day low
        days_ago = days_since_extreme(roll_low, is_min=True)
        if days_ago >= 4:
            # Find what the PRIOR 20-day low was (the level to fade above)
            prior_20d_low = roll_low.iloc[-2] if n > 2 else today_20d_low
            entry  = prior_20d_low + (highs[0] - lows[0]) * 0.001  # ~5 ticks above prior low
            stop   = lows[-1] - 0.01
            risk   = entry - stop
            target = entry + risk * 2
            conf   = min(90, 70 + (days_ago - 4) * 3)
            signals.append({
                'name'      : "Street Smarts: Turtle Soup (Long)",
                'source'    : "Raschke & Connors Ch.1",
                'signal'    : '▲ FADE 20-DAY LOW',
                'icon'      : '▲',
                'color'     : '#2ecc71',
                'confidence': conf,
                'value'     : f"20-day Low={today_20d_low:.2f}  Prior extreme {days_ago} sessions ago  (≥4 required)",
                'entry'     : f"BUY STOP: {entry:.2f} (5–10 ticks above prior 20-day low {prior_20d_low:.2f}). Good for today only.",
                'stop'      : f"{stop:.2f} (1 tick below today's new low = {lows[-1]:.2f})",
                'target'    : f"T1: Prior swing high area  T2: {target:.2f} (2× risk = {risk:.2f} pts)",
                'desc'      : (
                    f"Turtle Soup LONG setup detected.\n"
                    f"Today's low: {lows[-1]:.2f}\n"
                    f"20-day rolling low: {today_20d_low:.2f}\n"
                    f"Prior 20-day extreme: {days_ago} sessions ago (need ≥4 ✅)\n\n"
                    f"Raschke & Connors: The Turtle system buys 20-day lows.\n"
                    f"Most of these breakouts are false. Turtle Soup fades them.\n"
                    f"Trapped Turtle traders = your fuel on reversal.\n"
                    f"Modern equivalent: ICT Sellside Liquidity Raid."
                ),
            })

    # Turtle Soup SHORT (new 20-day high)
    if highs[-1] >= today_20d_high * 0.999:
        days_ago_h = days_since_extreme(roll_high, is_min=False)
        if days_ago_h >= 4:
            prior_20d_high = roll_high.iloc[-2] if n > 2 else today_20d_high
            entry  = prior_20d_high - (highs[0] - lows[0]) * 0.001
            stop   = highs[-1] + 0.01
            risk   = stop - entry
            target = entry - risk * 2
            conf   = min(90, 70 + (days_ago_h - 4) * 3)
            signals.append({
                'name'      : "Street Smarts: Turtle Soup (Short)",
                'source'    : "Raschke & Connors Ch.1",
                'signal'    : '▼ FADE 20-DAY HIGH',
                'icon'      : '▼',
                'color'     : '#e74c3c',
                'confidence': conf,
                'value'     : f"20-day High={today_20d_high:.2f}  Prior extreme {days_ago_h} sessions ago",
                'entry'     : f"SELL STOP: {entry:.2f} (5–10 ticks below prior 20-day high {prior_20d_high:.2f}). Today only.",
                'stop'      : f"{stop:.2f} (1 tick above today's new high = {highs[-1]:.2f})",
                'target'    : f"T1: Prior swing low area  T2: {target:.2f} (2× risk)",
                'desc'      : (
                    f"Turtle Soup SHORT setup detected.\n"
                    f"Today's high: {highs[-1]:.2f}\n"
                    f"20-day rolling high: {today_20d_high:.2f}\n"
                    f"Prior extreme: {days_ago_h} sessions ago (need ≥4 ✅)\n\n"
                    f"Fade the false 20-day high breakout.\n"
                    f"Trapped breakout buyers = your fuel on reversal."
                ),
            })

    # ── 2. TURTLE SOUP PLUS ONE ───────────────────────────────────────────
    # Yesterday made new 20-day extreme AND closed at/beyond the prior extreme
    if n >= 3:
        prev_low  = lows[-2]
        prev_high = highs[-2]
        prev_close = closes[-2]
        yest_20d_low  = roll_low.iloc[-2]
        yest_20d_high = roll_high.iloc[-2]

        # Plus One LONG: yesterday made new 20-day low AND closed AT or BELOW prior low
        if prev_low <= yest_20d_low * 1.001 and prev_close <= yest_20d_low * 1.002:
            prior_low_2 = roll_low.iloc[-3] if n > 3 else yest_20d_low
            days_ago_p1 = days_since_extreme(roll_low, is_min=True)
            if days_ago_p1 >= 3:
                entry  = prior_low_2 + 0.01
                stop   = min(prev_low, lows[-1]) - 0.01
                risk   = entry - stop
                target = entry + risk * 2
                signals.append({
                    'name'      : "Street Smarts: Turtle Soup Plus One (Long)",
                    'source'    : "Raschke & Connors Ch.1",
                    'signal'    : '▲ DAY-AFTER FADE (LONG)',
                    'icon'      : '▲',
                    'color'     : '#27ae60',
                    'confidence': 80,
                    'value'     : f"Yesterday: New 20d low={prev_low:.2f} AND closed at {prev_close:.2f} (at/below prior extreme)",
                    'entry'     : f"BUY STOP: {entry:.2f} (at prior 20-day low level {prior_low_2:.2f}). Valid today only.",
                    'stop'      : f"{stop:.2f} (below lower of Day1 or Day2 low)",
                    'target'    : f"T1: Prior swing high  T2: {target:.2f} (2× risk = {risk:.2f} pts)",
                    'desc'      : (
                        f"Turtle Soup Plus One LONG detected.\n"
                        f"Yesterday (Day 1): New 20-day low = {prev_low:.2f}\n"
                        f"Yesterday close = {prev_close:.2f} (at/below prior 20d extreme ✅)\n"
                        f"Today (Day 2): Place resting buy stop at prior 20d low level.\n\n"
                        f"More participants trapped than standard Turtle Soup:\n"
                        f"BOTH intraday breakout sellers AND close-on-breakout sellers\n"
                        f"are now underwater. Their covering = your profit."
                    ),
                })

    # ── 3. 80-20s ─────────────────────────────────────────────────────────
    # Yesterday opened in top/bottom 20% of range AND closed in opposite 80%
    if n >= 2:
        prev_o = opens[-2]; prev_h = highs[-2]
        prev_l = lows[-2];  prev_c = closes[-2]
        prev_rng = prev_h - prev_l
        if prev_rng > 0:
            open_pos  = (prev_o - prev_l) / prev_rng   # 0=bottom, 1=top
            close_pos = (prev_c - prev_l) / prev_rng

            # Buy setup: yesterday opened in bottom 20% AND closed in top 80%
            if open_pos <= 0.20 and close_pos >= 0.80:
                entry = prev_l - 0.01  # buy stop at yesterday's low
                # Today must probe below yesterday's low first (≥5 ticks)
                stop  = lows[-1] - 0.01 if lows[-1] < prev_l else prev_l * 0.995
                risk  = entry - stop
                tgt   = entry + abs(prev_rng) * 0.8
                signals.append({
                    'name'      : "Street Smarts: 80-20 (Buy Setup)",
                    'source'    : "Raschke & Connors Ch.3",
                    'signal'    : '▲ 80-20 REVERSAL BUY',
                    'icon'      : '▲',
                    'color'     : '#2ecc71',
                    'confidence': 72,
                    'value'     : f"Yesterday: Open pos={open_pos:.0%} (bottom 20% ✅)  Close pos={close_pos:.0%} (top 80% ✅)",
                    'entry'     : f"BUY STOP: {prev_l:.2f} (yesterday's low). Triggered only AFTER today probes ≥5 ticks below it first.",
                    'stop'      : f"{stop:.2f} (1 tick below today's low)",
                    'target'    : f"T1: {tgt:.2f} (yesterday's range extension)  Exit before 3:30 PM EST — day trade only.",
                    'desc'      : (
                        f"80-20 BUY Setup detected.\n"
                        f"Yesterday: Open={prev_o:.2f} (bottom {open_pos:.0%} of range) ✅\n"
                        f"Yesterday: Close={prev_c:.2f} (top {close_pos:.0%} of range) ✅\n\n"
                        f"Rule: Today must trade ≥5 ticks BELOW yesterday's low first\n"
                        f"(this is the false move — the Judas Swing). Then the buy\n"
                        f"stop triggers as price reverses back above yesterday's low.\n"
                        f"DAY TRADE ONLY — exit before 3:30 PM EST."
                    ),
                })

            # Sell setup: yesterday opened in top 20% AND closed in bottom 20%
            elif open_pos >= 0.80 and close_pos <= 0.20:
                entry = prev_h + 0.01  # sell stop at yesterday's high
                stop  = highs[-1] + 0.01 if highs[-1] > prev_h else prev_h * 1.005
                risk  = stop - entry
                tgt   = entry - abs(prev_rng) * 0.8
                signals.append({
                    'name'      : "Street Smarts: 80-20 (Sell Setup)",
                    'source'    : "Raschke & Connors Ch.3",
                    'signal'    : '▼ 80-20 REVERSAL SELL',
                    'icon'      : '▼',
                    'color'     : '#e74c3c',
                    'confidence': 72,
                    'value'     : f"Yesterday: Open pos={open_pos:.0%} (top 20% ✅)  Close pos={close_pos:.0%} (bottom 20% ✅)",
                    'entry'     : f"SELL STOP: {prev_h:.2f} (yesterday's high). Triggered only AFTER today probes ≥5 ticks above it first.",
                    'stop'      : f"{stop:.2f} (1 tick above today's high)",
                    'target'    : f"T1: {tgt:.2f} (yesterday's range extension down)  Day trade only.",
                    'desc'      : (
                        f"80-20 SELL Setup detected.\n"
                        f"Yesterday: Open={prev_o:.2f} (top {open_pos:.0%} of range) ✅\n"
                        f"Yesterday: Close={prev_c:.2f} (bottom {close_pos:.0%} of range) ✅\n\n"
                        f"Today probes above yesterday's high (Judas Swing), then reverses.\n"
                        f"Sell stop triggers as price falls back below yesterday's high.\n"
                        f"DAY TRADE ONLY — exit before 3:30 PM EST."
                    ),
                })

    # ── 4. MOMENTUM PINBALL ───────────────────────────────────────────────
    # RSI(2) of daily Close < 10 = buy, > 90 = sell
    if n >= 5:
        rsi2 = _rsi(df['Close'], min(2, n-1)).iloc[-1]

        if rsi2 < 10:
            signals.append({
                'name'      : "Street Smarts: Momentum Pinball (Buy)",
                'source'    : "Raschke & Connors Ch.4",
                'signal'    : '▲ PINBALL BUY — RSI OVERSOLD',
                'icon'      : '▲',
                'color'     : '#2ecc71',
                'confidence': 75,
                'value'     : f"RSI(2) = {rsi2:.1f} (below 10 = deeply oversold ✅)",
                'entry'     : f"BUY STOP above first hour's high on next session (9:30–10:30 AM). If not triggered by 11 AM: no trade.",
                'stop'      : f"First hour's LOW of next session — placed immediately on fill.",
                'target'    : f"T1: Day 2 close if profitable = carry overnight. Day 3 morning: exit near open or prior day's high.",
                'desc'      : (
                    f"Momentum Pinball BUY setup.\n"
                    f"RSI(2) of Close = {rsi2:.1f} (threshold: < 10)\n\n"
                    f"Raschke & Connors: Market has sold off too much in 2–3 days.\n"
                    f"Enter long when Day 2 breaks above the first hour's high.\n"
                    f"This confirms upward movement has already started.\n"
                    f"Hold max 3 days. 'Like fishing — small minnows most of the time.' — Linda"
                ),
            })
        elif rsi2 > 90:
            signals.append({
                'name'      : "Street Smarts: Momentum Pinball (Sell)",
                'source'    : "Raschke & Connors Ch.4",
                'signal'    : '▼ PINBALL SELL — RSI OVERBOUGHT',
                'icon'      : '▼',
                'color'     : '#e74c3c',
                'confidence': 75,
                'value'     : f"RSI(2) = {rsi2:.1f} (above 90 = deeply overbought ✅)",
                'entry'     : f"SELL STOP below first hour's low on next session. If not triggered by 11 AM: no trade.",
                'stop'      : f"First hour's HIGH of next session — placed immediately.",
                'target'    : f"T1: Day 2 close profitable = carry overnight short. Day 3: exit.",
                'desc'      : (
                    f"Momentum Pinball SELL setup.\n"
                    f"RSI(2) of Close = {rsi2:.1f} (threshold: > 90)\n\n"
                    f"Market has rallied too much in 2–3 days.\n"
                    f"Enter short when Day 2 breaks below first hour's low.\n"
                    f"Hold max 3 days."
                ),
            })

    # ── 5. THE ANTI ───────────────────────────────────────────────────────
    # %D trending up AND %K pulled back toward %D then hooked back up
    if n >= 15:
        pct_k, pct_d = _stoch(df['High'], df['Low'], df['Close'])
        k_now  = pct_k.iloc[-1]; k_prev = pct_k.iloc[-2]
        d_now  = pct_d.iloc[-1]; d_prev = pct_d.iloc[-2]
        d_prev2 = pct_d.iloc[-3]

        d_rising = d_now > d_prev > d_prev2  # %D trending up
        k_was_below = pct_k.iloc[-3] < pct_d.iloc[-3]  # %K was below %D
        k_hooking_up = k_now > k_prev  # %K now hooking up

        if d_rising and k_was_below and k_hooking_up and k_now < d_now + 15:
            entry  = highs[-1] + 0.01
            stop   = lows[-1]  - 0.01
            risk   = entry - stop
            target = entry + risk * 2
            signals.append({
                'name'      : "Street Smarts: The Anti (Bullish)",
                'source'    : "Raschke & Connors Ch.5",
                'signal'    : '▲ ANTI BUY — STOCH HOOK',
                'icon'      : '▲',
                'color'     : '#27ae60',
                'confidence': 78,
                'value'     : f"%K={k_now:.1f}  %D={d_now:.1f}  %D rising: ✅  %K hooking up: ✅",
                'entry'     : f"BUY STOP: {entry:.2f} (1 tick above prior bar's high as %K hooks up)",
                'stop'      : f"{stop:.2f} (below entry bar low or recent swing low)",
                'target'    : f"T1: Range expansion bar within 3–4 bars = EXIT ALL. T2: Max hold = 4 bars.",
                'desc'      : (
                    f"The Anti BUY setup detected.\n"
                    f"Stochastic (%K=7, %D=10):\n"
                    f"  %D = {d_now:.1f} (trending UP ✅)\n"
                    f"  %K = {k_now:.1f} (was below %D, now hooking UP ✅)\n\n"
                    f"Raschke: Two timeframes of momentum aligning = positive feedback.\n"
                    f"The %D trend is the institutional direction.\n"
                    f"The %K pullback and hook = short-term correction ending.\n"
                    f"Exit on the first range expansion bar — that IS the climax."
                ),
            })

        # Anti SELL: %D trending DOWN, %K hooked back down
        d_falling = d_now < d_prev < d_prev2
        k_was_above = pct_k.iloc[-3] > pct_d.iloc[-3]
        k_hooking_down = k_now < k_prev

        if d_falling and k_was_above and k_hooking_down and k_now > d_now - 15:
            entry  = lows[-1] - 0.01
            stop   = highs[-1] + 0.01
            risk   = stop - entry
            target = entry - risk * 2
            signals.append({
                'name'      : "Street Smarts: The Anti (Bearish)",
                'source'    : "Raschke & Connors Ch.5",
                'signal'    : '▼ ANTI SELL — STOCH HOOK',
                'icon'      : '▼',
                'color'     : '#e74c3c',
                'confidence': 78,
                'value'     : f"%K={k_now:.1f}  %D={d_now:.1f}  %D falling: ✅  %K hooking down: ✅",
                'entry'     : f"SELL STOP: {entry:.2f} (1 tick below prior bar's low as %K hooks down)",
                'stop'      : f"{stop:.2f} (above entry bar high or recent swing high)",
                'target'    : f"T1: Range expansion bar = EXIT ALL. Max hold = 4 bars.",
                'desc'      : (
                    f"The Anti SELL setup detected.\n"
                    f"%D = {d_now:.1f} (trending DOWN ✅)\n"
                    f"%K = {k_now:.1f} (was above %D, now hooking DOWN ✅)\n\n"
                    f"Two momentum timeframes aligning in the bearish direction."
                ),
            })

    # ── 6. HOLY GRAIL (LBR version) ───────────────────────────────────────
    # ADX > 30 AND rising, price pulls back to touch 20 EMA
    if n >= 20:
        adx_s, pdi_s, ndi_s = _adx(df['High'], df['Low'], df['Close'])
        adx_now  = adx_s.iloc[-1];  adx_prev = adx_s.iloc[-2]
        pdi_now  = pdi_s.iloc[-1];  ndi_now  = ndi_s.iloc[-1]
        ema20_s  = _ema(df['Close'], min(20, n-1))
        ema20_now = ema20_s.iloc[-1]
        adx_rising = adx_now > adx_prev

        # Bull trend: ADX>30 rising, +DI>-DI, price touched or crossed EMA
        if adx_now > 30 and pdi_now > ndi_now:
            price_near_ema = abs(curr - ema20_now) / ema20_now < 0.005
            price_crossed  = (lows[-1] <= ema20_now <= highs[-1])
            if price_near_ema or price_crossed:
                entry  = highs[-1] + 0.01
                stop   = lows[-1]  - 0.01
                risk   = entry - stop
                target = entry + risk * 3
                conf   = 82 if adx_rising else 70
                signals.append({
                    'name'      : "Street Smarts: Holy Grail (Bull)",
                    'source'    : "Raschke & Connors Ch.6",
                    'signal'    : '▲ HOLY GRAIL — EMA PULLBACK',
                    'icon'      : '▲',
                    'color'     : '#f1c40f',
                    'confidence': conf,
                    'value'     : f"ADX={adx_now:.1f} (>30 ✅)  +DI={pdi_now:.1f} > -DI={ndi_now:.1f} ✅  EMA20={ema20_now:.2f}  Price touched ✅",
                    'entry'     : f"BUY STOP: {entry:.2f} (1 tick above prior bar's high at the 20 EMA)",
                    'stop'      : f"{stop:.2f} (at the newly formed swing low — the pullback low)",
                    'target'    : f"T1: Prior swing high (scale 50%).  T2: Trail with ADX continuation. Risk={risk:.2f}",
                    'desc'      : (
                        f"Holy Grail BUY setup — LBR version.\n"
                        f"ADX(14) = {adx_now:.1f} ({'rising ✅' if adx_rising else 'flat'})\n"
                        f"+DI = {pdi_now:.1f} > -DI = {ndi_now:.1f} (bull trend ✅)\n"
                        f"20 EMA = {ema20_now:.2f} (price is touching it now)\n\n"
                        f"Raschke: 'ADX turning down is NOT reversal — it is consolidation.'\n"
                        f"This pullback to the EMA is the institutional reload point.\n"
                        f"Three frameworks confirm: Raschke, Carter, and ICT all identify this."
                    ),
                })

        # Bear trend: ADX>30, -DI>+DI, price touched EMA from below
        if adx_now > 30 and ndi_now > pdi_now:
            price_near_ema = abs(curr - ema20_now) / ema20_now < 0.005
            price_crossed  = (lows[-1] <= ema20_now <= highs[-1])
            if price_near_ema or price_crossed:
                entry  = lows[-1] - 0.01
                stop   = highs[-1] + 0.01
                risk   = stop - entry
                target = entry - risk * 3
                conf   = 82 if adx_rising else 70
                signals.append({
                    'name'      : "Street Smarts: Holy Grail (Bear)",
                    'source'    : "Raschke & Connors Ch.6",
                    'signal'    : '▼ HOLY GRAIL — EMA RALLY FADE',
                    'icon'      : '▼',
                    'color'     : '#e74c3c',
                    'confidence': conf,
                    'value'     : f"ADX={adx_now:.1f} (>30 ✅)  -DI={ndi_now:.1f} > +DI={pdi_now:.1f} ✅  EMA20={ema20_now:.2f}",
                    'entry'     : f"SELL STOP: {entry:.2f} (1 tick below prior bar's low at the 20 EMA)",
                    'stop'      : f"{stop:.2f} (above the swing high of the pullback rally)",
                    'target'    : f"T1: Prior swing low. T2: Trail with ADX. Risk={risk:.2f}",
                    'desc'      : (
                        f"Holy Grail SELL setup.\n"
                        f"ADX(14) = {adx_now:.1f}  -DI={ndi_now:.1f} > +DI={pdi_now:.1f} (downtrend ✅)\n"
                        f"20 EMA = {ema20_now:.2f} — price is rallying into EMA resistance."
                    ),
                })

    # ── 7. ADX GAPPER ────────────────────────────────────────────────────
    # ADX>30, trend confirmed by DI lines, today gapped against the trend
    if n >= 3:
        try:
            adx_s2, pdi_s2, ndi_s2 = _adx(df['High'], df['Low'], df['Close'])
            adx2 = adx_s2.iloc[-1]; pdi2 = pdi_s2.iloc[-1]; ndi2 = ndi_s2.iloc[-1]
            prev_low2 = lows[-2]; prev_high2 = highs[-2]
            today_open = opens[-1]

            # Bull gapper: ADX>30, +DI>-DI, today gapped below yesterday's low
            if adx2 > 30 and pdi2 > ndi2 and today_open < prev_low2:
                gap_size = prev_low2 - today_open
                entry    = prev_low2 + 0.01
                stop     = lows[-1] - 0.01
                risk     = entry - stop
                target   = entry + risk * 2.5
                signals.append({
                    'name'      : "Street Smarts: ADX Gapper (Bull)",
                    'source'    : "Raschke & Connors Ch.7",
                    'signal'    : '▲ ADX GAPPER — BUY THE GAP',
                    'icon'      : '▲',
                    'color'     : '#3498db',
                    'confidence': 76,
                    'value'     : f"ADX={adx2:.1f} (+DI={pdi2:.1f} > -DI={ndi2:.1f} ✅)  Gap down: {gap_size:.2f} pts below yesterday's low",
                    'entry'     : f"BUY STOP: {entry:.2f} (at yesterday's low {prev_low2:.2f})",
                    'stop'      : f"{stop:.2f} (1 tick below today's morning low = {lows[-1]:.2f})",
                    'target'    : f"T1: Yesterday's close {closes[-2]:.2f}  T2: {target:.2f} (2.5× risk)",
                    'desc'      : (
                        f"ADX Gapper BUY detected.\n"
                        f"ADX = {adx2:.1f} (>30, bull trend: +DI > -DI ✅)\n"
                        f"Today gapped BELOW yesterday's low by {gap_size:.2f} pts\n"
                        f"(against the confirmed bull trend)\n\n"
                        f"Raschke: In a strong trend, counter-trend gaps are short-lived.\n"
                        f"Institutions use the gap to accumulate at better prices\n"
                        f"before the trend resumes. The ADX filter is what makes this work."
                    ),
                })

            # Bear gapper: ADX>30, -DI>+DI, today gapped above yesterday's high
            if adx2 > 30 and ndi2 > pdi2 and today_open > prev_high2:
                gap_size = today_open - prev_high2
                entry    = prev_high2 - 0.01
                stop     = highs[-1] + 0.01
                risk     = stop - entry
                target   = entry - risk * 2.5
                signals.append({
                    'name'      : "Street Smarts: ADX Gapper (Bear)",
                    'source'    : "Raschke & Connors Ch.7",
                    'signal'    : '▼ ADX GAPPER — SELL THE GAP',
                    'icon'      : '▼',
                    'color'     : '#e74c3c',
                    'confidence': 76,
                    'value'     : f"ADX={adx2:.1f} (-DI={ndi2:.1f} > +DI={pdi2:.1f} ✅)  Gap up: {gap_size:.2f} pts above yesterday's high",
                    'entry'     : f"SELL STOP: {entry:.2f} (at yesterday's high {prev_high2:.2f})",
                    'stop'      : f"{stop:.2f} (1 tick above today's opening high)",
                    'target'    : f"T1: Yesterday's close {closes[-2]:.2f}  T2: {target:.2f}",
                    'desc'      : (
                        f"ADX Gapper SELL detected.\n"
                        f"ADX = {adx2:.1f} (>30, bear trend: -DI > +DI ✅)\n"
                        f"Today gapped ABOVE yesterday's high by {gap_size:.2f} pts (against bear trend)\n\n"
                        f"Fade the gap against the confirmed downtrend."
                    ),
                })
        except Exception:
            pass

    # ── 8. WHIPLASH ───────────────────────────────────────────────────────
    # Today gapped below yesterday's low AND reversed to close above open, top 50%
    if n >= 2:
        prev_low3 = lows[-2]
        today_o   = opens[-1]; today_h = highs[-1]
        today_l   = lows[-1];  today_c = closes[-1]
        today_rng = today_h - today_l

        gapped_lower = today_o < prev_low3
        closed_above_open = today_c > today_o
        in_top_half = today_rng > 0 and (today_c - today_l) / today_rng >= 0.50

        if gapped_lower and closed_above_open and in_top_half:
            ibs = (today_c - today_l) / today_rng if today_rng > 0 else 0.5
            signals.append({
                'name'      : "Street Smarts: Whiplash (MOC Buy)",
                'source'    : "Raschke & Connors Ch.8",
                'signal'    : '▲ WHIPLASH — BUY MOC',
                'icon'      : '▲',
                'color'     : '#9b59b6',
                'confidence': 74,
                'value'     : f"Gapped below yesterday's low ✅  Closed above open ✅  Top {(1-in_top_half)*100:.0f}% of range ✅  IBS={ibs:.2f}",
                'entry'     : f"BUY MOC (Market-On-Close) today. Both conditions confirmed: gap + reversal.",
                'stop'      : f"If next morning opens BELOW today's close {today_c:.2f}: EXIT IMMEDIATELY at open.",
                'target'    : f"T1: Morning follow-through — exit first 15–30 min of next session. Gap open up = exit at-market.",
                'desc'      : (
                    f"Whiplash BUY setup confirmed.\n"
                    f"✅ Today gapped below yesterday's low ({prev_low3:.2f})\n"
                    f"✅ Today closed above the open ({today_o:.2f})\n"
                    f"✅ Closed in top 50% of today's range (IBS={ibs:.2f})\n\n"
                    f"Raschke: The gap created the initial panic (the whiplash).\n"
                    f"The reversal close proves smart money absorbed the selling.\n"
                    f"Enter MOC tonight. Bad open tomorrow = exit immediately at open."
                ),
            })

    # ── 9. THREE-DAY UNFILLED GAP ─────────────────────────────────────────
    # A gap down that was NOT filled during the day session — flag for 3 days
    if n >= 2:
        # Check if today gapped down AND gap was NOT filled (high < yesterday's low)
        prev_low4 = lows[-2]
        today_o4  = opens[-1]; today_h4 = highs[-1]

        gapped_down4 = today_o4 < prev_low4
        unfilled     = today_h4 < prev_low4  # today's high never reached yesterday's low

        if gapped_down4 and unfilled:
            entry  = today_h4 + 0.01  # buy stop above gap-day high
            stop   = lows[-1] - 0.01
            risk   = entry - stop
            target = prev_low4 + (prev_low4 - lows[-1])  # project to pre-gap level
            signals.append({
                'name'      : "Street Smarts: Three-Day Unfilled Gap",
                'source'    : "Raschke & Connors Ch.9",
                'signal'    : '▲ UNFILLED GAP — 3-DAY RESTING BUY',
                'icon'      : '▲',
                'color'     : '#1abc9c',
                'confidence': 68,
                'value'     : f"Gap: Today opened {today_o4:.2f} vs yesterday's low {prev_low4:.2f}  Today's high {today_h4:.2f} < yesterday's low = UNFILLED ✅",
                'entry'     : f"RESTING BUY STOP: {entry:.2f} (1 tick above today's high {today_h4:.2f}). Valid for 3 trading sessions — cancel if not triggered.",
                'stop'      : f"{stop:.2f} (1 tick below today's low = {lows[-1]:.2f})",
                'target'    : f"T1: Pre-gap level {prev_low4:.2f} (scale 50%).  T2: {target:.2f} (measure gap and project)",
                'desc'      : (
                    f"Three-Day Unfilled Gap (BUY) setup.\n"
                    f"Today gapped DOWN: Open={today_o4:.2f} < Yesterday's low={prev_low4:.2f}\n"
                    f"Gap unfilled: Today's high={today_h4:.2f} never reached {prev_low4:.2f}\n\n"
                    f"Raschke: Unfilled gaps are magnetic — price is 'owed' trades at\n"
                    f"those levels. When the gap begins to close, momentum\n"
                    f"typically accompanies the move.\n"
                    f"Place resting buy stop — valid 3 days. Cancel if not triggered."
                ),
            })

    # ── 10. NEWS REVERSAL (gap-detection version) ─────────────────────────
    # Today's open gapped significantly vs yesterday's range AND reversed
    if n >= 2:
        prev_h5 = highs[-2]; prev_l5 = lows[-2]
        today_o5 = opens[-1]; today_c5 = closes[-1]
        today_h5 = highs[-1]; today_l5 = lows[-1]

        # Bull gap reversal: opened above yesterday's high but reversed sharply
        gap_up  = today_o5 > prev_h5
        reversed_down = today_c5 < prev_h5  # closed back below yesterday's high
        large_gap = (today_o5 - prev_h5) / prev_h5 > 0.002  # at least 0.2%

        if gap_up and reversed_down and large_gap:
            gap_pts = today_o5 - prev_h5
            entry   = prev_h5 - 0.01  # sell stop below yesterday's high
            stop    = today_h5 + 0.01
            risk    = stop - entry
            target  = entry - risk * 2
            signals.append({
                'name'      : "Street Smarts: News Reversal (Short)",
                'source'    : "Raschke & Connors Ch.12",
                'signal'    : '▼ NEWS REVERSAL — FADE THE GAP UP',
                'icon'      : '▼',
                'color'     : '#e74c3c',
                'confidence': 71,
                'value'     : f"Gapped up {gap_pts:.2f} pts above yesterday's high ({prev_h5:.2f}), then reversed and closed at {today_c5:.2f}",
                'entry'     : f"SELL STOP: {entry:.2f} (1–3 ticks below yesterday's high {prev_h5:.2f})",
                'stop'      : f"{stop:.2f} (1 tick above today's high = {today_h5:.2f})",
                'target'    : f"T1: Prior support  T2: {target:.2f} (2× risk = {risk:.2f} pts)",
                'desc'      : (
                    f"News Reversal SHORT detected.\n"
                    f"Today gapped UP {gap_pts:.2f} pts above yesterday's high ({prev_h5:.2f})\n"
                    f"Then REVERSED and closed at {today_c5:.2f} (back below the level)\n\n"
                    f"Raschke: 'Logic will lead you to the poorhouse.'\n"
                    f"The market spiked on the news (logical direction)\n"
                    f"then reversed = news was already priced in.\n"
                    f"The initial spike attracted late buyers who are now trapped."
                ),
            })

        # Bear gap reversal: opened below yesterday's low but reversed sharply up
        gap_down5 = today_o5 < prev_l5
        reversed_up = today_c5 > prev_l5
        large_gap5 = (prev_l5 - today_o5) / prev_l5 > 0.002

        if gap_down5 and reversed_up and large_gap5:
            gap_pts5 = prev_l5 - today_o5
            entry5   = prev_l5 + 0.01
            stop5    = today_l5 - 0.01
            risk5    = entry5 - stop5
            target5  = entry5 + risk5 * 2
            signals.append({
                'name'      : "Street Smarts: News Reversal (Long)",
                'source'    : "Raschke & Connors Ch.12",
                'signal'    : '▲ NEWS REVERSAL — FADE THE GAP DOWN',
                'icon'      : '▲',
                'color'     : '#2ecc71',
                'confidence': 71,
                'value'     : f"Gapped down {gap_pts5:.2f} pts below yesterday's low ({prev_l5:.2f}), reversed up to close {today_c5:.2f}",
                'entry'     : f"BUY STOP: {entry5:.2f} (1–3 ticks above yesterday's low {prev_l5:.2f})",
                'stop'      : f"{stop5:.2f} (1 tick below today's low = {today_l5:.2f})",
                'target'    : f"T1: Prior resistance  T2: {target5:.2f} (2× risk)",
                'desc'      : (
                    f"News Reversal LONG detected.\n"
                    f"Today gapped DOWN {gap_pts5:.2f} pts below yesterday's low ({prev_l5:.2f})\n"
                    f"Then REVERSED and closed at {today_c5:.2f} (back above the level)\n\n"
                    f"Bad news spike immediately reversed = smart money absorbed the selling.\n"
                    f"Trapped sellers are your fuel as the market rises."
                ),
            })

    # Sort by confidence
    signals.sort(key=lambda x: x['confidence'], reverse=True)
    return signals



# ─────────────────────────────────────────────────────────────────────────────
#  LEVEL 1 — PATTERN COMPLETION FORECASTING ENGINE
#  Source: Bulkowski Encyclopedia of Chart Patterns (2005)
#  For every detected pattern, computes:
#   1. Completion probability (from 38,500 sample database)
#   2. Expected move % and target prices
#   3. Time to completion estimate
#   4. Throwback/pullback probability and price
#   5. Failure risk assessment
#   6. Best conditions for this pattern to work
# ─────────────────────────────────────────────────────────────────────────────

def compute_pattern_forecast(pat, df, market_context='bull'):
    """
    Compute a full probabilistic forecast for a detected pattern.

    Parameters:
        pat            : detected pattern dict from detect_patterns()
        df             : OHLC DataFrame
        market_context : 'bull' or 'bear' (detected from 200-day MA)

    Returns dict with all forecast fields.
    """
    import re as _re

    name    = pat.get('name', '')
    current = df['Close'].values[-1]
    neckline   = pat.get('neckline')
    pat_low    = pat.get('pattern_low')
    pat_high   = pat.get('pattern_high')
    confidence = pat.get('confidence', 60)
    direction  = pat.get('direction', '')
    is_bull    = 'BULL' in direction.upper()

    # ── Get Bulkowski database stats ──────────────────────────────────────
    db_match = None
    for key in PATTERNS_DB:
        if pat['name'] in key or key in pat['name']:
            db_match = PATTERNS_DB[key]
            break
    if not db_match:
        # Try partial match
        pat_words = pat['name'].split()
        for key in PATTERNS_DB:
            if any(w in key for w in pat_words[:2]):
                db_match = PATTERNS_DB[key]
                break

    stats = {}
    if db_match:
        mkt_key = 'bull_market' if market_context == 'bull' else 'bear_market'
        raw_stats = db_match.get('stats', {}).get(mkt_key, {})
        # Parse numeric values
        for field, raw in raw_stats.items():
            try:
                nums = _re.findall(r'\d+\.?\d*', str(raw))
                stats[field] = float(nums[0]) if nums else 0
            except Exception:
                stats[field] = 0

    # ── Core stats ────────────────────────────────────────────────────────
    avg_rise         = stats.get('avg_rise', 30 if is_bull else 20)
    failure_rate     = stats.get('breakeven_failure_rate', 10)
    throwback_rate   = stats.get('throwback_rate', 50)
    throwback_days   = stats.get('avg_throwback_days', 11)
    samples          = int(stats.get('samples', 0))
    perf_rank        = db_match.get('stats', {}).get(
        'bull_market' if market_context == 'bull' else 'bear_market',
        {}).get('performance_rank', 'Fair') if db_match else 'Fair'

    # ── Completion probability ─────────────────────────────────────────────
    # Base from pattern confidence + Bulkowski failure rate
    base_prob = confidence * (1 - failure_rate / 100)
    # Adjust for market context
    if market_context == 'bull' and is_bull:
        base_prob = min(95, base_prob * 1.1)
    elif market_context == 'bear' and not is_bull:
        base_prob = min(95, base_prob * 1.1)
    else:
        base_prob = base_prob * 0.85  # counter-trend = lower probability
    completion_prob = round(base_prob)

    # ── Price targets ──────────────────────────────────────────────────────
    if neckline and pat_low and is_bull:
        pattern_height = neckline - pat_low
        target_1 = neckline + pattern_height           # 100% measure rule
        target_2 = neckline + pattern_height * 1.5    # 150% extended
        target_3 = neckline + pattern_height * 2.0    # 200% maximum
        move_to_t1 = (target_1 - current) / current * 100
        move_to_t2 = (target_2 - current) / current * 100
    elif neckline and pat_high and not is_bull:
        pattern_height = pat_high - neckline
        target_1 = neckline - pattern_height
        target_2 = neckline - pattern_height * 1.5
        target_3 = neckline - pattern_height * 2.0
        move_to_t1 = (target_1 - current) / current * 100
        move_to_t2 = (target_2 - current) / current * 100
    else:
        # Fallback using avg_rise from database
        if is_bull:
            target_1 = current * (1 + avg_rise / 100)
            target_2 = current * (1 + avg_rise * 1.5 / 100)
            target_3 = current * (1 + avg_rise * 2.0 / 100)
        else:
            target_1 = current * (1 - avg_rise / 100)
            target_2 = current * (1 - avg_rise * 1.5 / 100)
            target_3 = current * (1 - avg_rise * 2.0 / 100)
        pattern_height = abs(target_1 - current)
        move_to_t1 = avg_rise if is_bull else -avg_rise
        move_to_t2 = move_to_t1 * 1.5

    # ── Throwback/pullback forecast ────────────────────────────────────────
    throwback_prob   = round(throwback_rate)
    throwback_target = neckline if neckline else current * 0.98 if is_bull else current * 1.02
    throwback_action = ("Hold if price closes ABOVE neckline during throwback.\n"
                        "Exit if price closes BELOW neckline — pattern failed." if is_bull else
                        "Hold if price closes BELOW neckline during pullback.\n"
                        "Exit if price closes ABOVE neckline — pattern failed.")

    # ── Time estimate ──────────────────────────────────────────────────────
    # Based on Bulkowski's typical completion times
    time_estimates = {
        'Head-and-Shoulders': 20,
        'Double Bottom': 15,
        'Double Top': 15,
        'Triple': 25,
        'Triangle': 30,
        'Cup': 45,
        'Flag': 5,
        'Wedge': 10,
        'Measured Move': 20,
    }
    est_days = 20  # default
    for key, days in time_estimates.items():
        if key.lower() in name.lower():
            est_days = days
            break

    # ── Failure scenarios ──────────────────────────────────────────────────
    failure_scenarios = []
    if is_bull:
        failure_scenarios = [
            f"Price fails to close above neckline ({neckline:.2f}) within next {est_days} days",
            f"Throwback occurs AND price closes below neckline ({throwback_target:.2f})",
            f"Volume dries up on breakout (weak institutional participation)",
            f"Broad market enters strong downtrend (Nifty breaks 200-day MA)",
        ] if neckline else [
            "Pattern fails to develop the required swing structure",
            "Price breaks back below the pattern low",
            "Broad market deteriorates sharply",
        ]
    else:
        failure_scenarios = [
            f"Price fails to close below neckline ({neckline:.2f}) within {est_days} days",
            f"Pullback occurs AND price closes above neckline",
            f"Broad market begins new bull run (Nifty reclaims 200-day MA)",
        ] if neckline else [
            "Pattern fails to develop the required structure",
            "Price breaks back above the pattern high",
        ]

    # ── Best conditions filter ─────────────────────────────────────────────
    best_conditions = []
    if db_match:
        best_conditions = db_match.get('best_performance', [])
    if not best_conditions:
        best_conditions = [
            f"{'Bull' if is_bull else 'Bear'} market confirmed (price {'above' if is_bull else 'below'} 200-day MA)",
            "Pattern height above 1-month median = better performance",
            "Breakout on above-average volume = stronger move",
            "Pattern forms at key support/resistance level",
        ]

    # ── Target reliability ─────────────────────────────────────────────────
    target_rel = db_match.get('target_reliability', '65%') if db_match else '60%'
    try:
        target_rel_num = float(_re.findall(r'\d+', str(target_rel))[0])
    except Exception:
        target_rel_num = 65

    # ── Conviction grade ───────────────────────────────────────────────────
    score = (completion_prob * 0.4 +
             (100 - failure_rate) * 0.3 +
             min(samples / 10, 10) * 3 +
             target_rel_num * 0.2)
    if score >= 85:   grade = 'A+ — EXCEPTIONAL'; grade_col = '#2ecc71'
    elif score >= 75: grade = 'A  — HIGH CONVICTION'; grade_col = '#27ae60'
    elif score >= 65: grade = 'B  — MODERATE'; grade_col = '#f1c40f'
    elif score >= 55: grade = 'C  — LOW CONVICTION'; grade_col = '#e67e22'
    else:             grade = 'D  — SKIP'; grade_col = '#e74c3c'

    return {
        # Core
        'pattern_name':       name,
        'direction':          direction,
        'is_bull':            is_bull,
        'current_price':      current,
        'market_context':     market_context,
        # Probability
        'completion_prob':    completion_prob,
        'failure_rate':       failure_rate,
        'samples':            samples,
        'performance_rank':   perf_rank,
        # Targets
        'neckline':           neckline,
        'pattern_height':     pattern_height,
        'target_1':           target_1,
        'target_2':           target_2,
        'target_3':           target_3,
        'move_to_t1_pct':     round(move_to_t1, 1),
        'move_to_t2_pct':     round(move_to_t2, 1),
        'target_reliability': target_rel_num,
        # Throwback
        'throwback_prob':     throwback_prob,
        'throwback_target':   throwback_target,
        'throwback_days':     int(throwback_days),
        'throwback_action':   throwback_action,
        # Time
        'est_completion_days': est_days,
        # Failure
        'failure_scenarios':  failure_scenarios,
        # Best conditions
        'best_conditions':    best_conditions,
        # Grade
        'conviction_grade':   grade,
        'conviction_color':   grade_col,
        'conviction_score':   round(score),
        # Measure rule
        'measure_rule': db_match.get('measure_rule', '') if db_match else '',
    }



# ─────────────────────────────────────────────────────────────────────────────
#  BROOKS PA FORECAST ENGINE
#  Source: Trading Price Action Trends — Al Brooks (Wiley, 2012)
#  Computes context-adjusted signal quality score, targets, time rules,
#  failure signals, and position sizing guidance for every Brooks signal.
# ─────────────────────────────────────────────────────────────────────────────

# Base quality scores from Brooks text — how strongly he endorses each setup
BROOKS_BASE_SCORES = {
    'Breakout Pullback':           78,
    'High 1':                      62,
    'High 2':                      75,
    'Two-Bar Reversal':            68,
    'Wedge Reversal':              70,
    'Failed Breakout':             73,
    'Measured Move':               70,
    'MA Gap Bar':                  72,
    'Inside Bar':                  65,
    'ii Pattern':                  80,   # doubled energy
    'Final Flag':                  72,
    'Spike and Channel':           68,
    'Trend Line Break':            75,
    'Trend from the Open':         80,
    'Breakout Pullback Long':      78,
    'Breakout Pullback Short':     78,
    'Bull Trend':                  80,
    'Bear Trend':                  80,
    'Stoch Hook':                  70,
}

# Brooks' explicit max hold time rules (in bars)
BROOKS_MAX_HOLD = {
    'reversal':     4,    # Ch.6: "exit reversal trades if no reward in 4 bars"
    'continuation': 0,    # trail indefinitely in strong trends
    'breakout':    10,    # give breakouts room to develop
    'climax':       2,    # climax moves — take profit fast
    'retracement': 8,    # pullback entries — hold through noise
}

# Brooks position sizing guidance
BROOKS_SIZE_RULES = {
    'with-trend':     'FULL SIZE — trading with institutional order flow',
    'counter-trend':  'HALF SIZE — fading the trend is lower probability',
    'breakout':       'FULL SIZE first half, HALF SIZE second half',
    'reversal':       'HALF SIZE — wait for second entry confirmation',
    'both':           'STANDARD — direction from context',
    'with_trend':     'FULL SIZE — with institutional order flow',
}


def compute_brooks_forecast(sig, df):
    """
    Compute a full Brooks PA forecast for a detected signal.

    Parameters:
        sig : detected Brooks signal dict from detect_brooks_signals()
        df  : OHLC DataFrame

    Returns dict with complete forecast.
    """
    import re as _re

    name      = sig.get('name', '')
    signal    = sig.get('signal', '')
    source    = sig.get('source', '')
    confidence= sig.get('confidence', 65)
    entry_txt = sig.get('entry', '')
    stop_txt  = sig.get('stop', '')
    target_txt= sig.get('target', '')
    desc      = sig.get('desc', '')
    icon      = sig.get('icon', '◆')

    closes = df['Close'].values
    highs  = df['High'].values
    lows   = df['Low'].values
    opens  = df['Open'].values
    n      = len(df)
    curr   = closes[-1]

    # ── Compute indicators for context scoring ─────────────────────────────
    ema20_s = _ema(df['Close'], min(20, n-1))
    ema20   = ema20_s.iloc[-1]
    ema_rising = ema20_s.iloc[-1] > ema20_s.iloc[-2] if n > 2 else True

    avg_bar = np.mean([highs[i] - lows[i] for i in range(max(0,n-20), n)])
    curr_bar= highs[-1] - lows[-1]
    bar_is_large = curr_bar > avg_bar * 1.2

    # ADX for trend strength
    try:
        adx_s, pdi_s, ndi_s = _adx(df['High'], df['Low'], df['Close'])
        adx   = adx_s.iloc[-1]
        pdi   = pdi_s.iloc[-1]
        ndi   = ndi_s.iloc[-1]
        adx_rising = adx_s.iloc[-1] > adx_s.iloc[-2] if n > 2 else False
        trend_strength = (
            'STRONG'   if adx > 35 else
            'MODERATE' if adx > 20 else
            'WEAK'
        )
    except Exception:
        adx = 20; pdi = 25; ndi = 25
        adx_rising = False
        trend_strength = 'MODERATE'

    # Always-in direction
    always_in_bull = curr > ema20 and ema_rising
    always_in_bear = curr < ema20 and not ema_rising

    # Is the signal with or against the trend?
    is_bull_signal = '▲' in signal or 'BULL' in signal.upper() or 'BUY' in signal.upper()
    is_bear_signal = '▼' in signal or 'BEAR' in signal.upper() or 'SELL' in signal.upper()

    with_trend = (is_bull_signal and always_in_bull) or \
                 (is_bear_signal and always_in_bear)
    counter_trend = (is_bull_signal and always_in_bear) or \
                    (is_bear_signal and always_in_bull)

    # ── Base score from signal type ────────────────────────────────────────
    base_score = confidence
    for key, score in BROOKS_BASE_SCORES.items():
        if key.lower() in name.lower():
            base_score = score
            break

    # ── Context scoring matrix ─────────────────────────────────────────────
    context_items = []
    score_adj     = 0

    # 1. Always-in direction
    if with_trend:
        score_adj += 12
        context_items.append(('✅', 'With always-in direction', +12))
    elif counter_trend:
        score_adj -= 12
        context_items.append(('❌', 'Against always-in direction (counter-trend)', -12))
    else:
        context_items.append(('◆', 'Neutral — direction unclear', 0))

    # 2. ADX strength
    if adx > 30 and adx_rising:
        score_adj += 10
        context_items.append(('✅', f'ADX={adx:.1f} strong and rising (ideal)', +10))
    elif adx > 20:
        score_adj += 4
        context_items.append(('◆', f'ADX={adx:.1f} moderate trend', +4))
    elif adx < 15:
        score_adj -= 8
        context_items.append(('❌', f'ADX={adx:.1f} very weak — choppy market', -8))
    else:
        context_items.append(('◆', f'ADX={adx:.1f} — neutral trend strength', 0))

    # 3. Price vs 20 EMA
    ema_dist_pct = abs(curr - ema20) / ema20 * 100
    if ema_dist_pct < 0.5:
        score_adj += 8
        context_items.append(('✅', f'Price at 20 EMA ({ema20:.2f}) — ideal pullback zone', +8))
    elif ema_dist_pct < 2.0:
        score_adj += 4
        context_items.append(('◆', f'Price near 20 EMA ({ema20:.2f}) — good zone', +4))
    elif ema_dist_pct > 5.0:
        score_adj -= 5
        context_items.append(('⚠', f'Price far from 20 EMA ({ema_dist_pct:.1f}%) — extended', -5))
    else:
        context_items.append(('◆', f'Price {ema_dist_pct:.1f}% from 20 EMA', 0))

    # 4. Signal bar quality
    body_size  = abs(closes[-1] - opens[-1])
    body_ratio = body_size / curr_bar if curr_bar > 0 else 0
    if body_ratio >= 0.6:
        score_adj += 7
        context_items.append(('✅', f'Strong signal bar (body={body_ratio:.0%} of range)', +7))
    elif body_ratio >= 0.4:
        score_adj += 3
        context_items.append(('◆', f'Moderate signal bar (body={body_ratio:.0%})', +3))
    else:
        score_adj -= 5
        context_items.append(('❌', f'Weak signal bar (body={body_ratio:.0%}) — doji/indecision', -5))

    # 5. Trend from open (if applicable)
    if 'Trend from Open' in name or 'Trend from the Open' in name:
        score_adj += 8
        context_items.append(('✅', 'Trend from Open — institutional mandate clear', +8))

    # 6. ii pattern bonus
    if 'ii' in name.lower():
        score_adj += 5
        context_items.append(('✅', 'ii pattern — doubled energy compression', +5))

    # Final score
    quality_score = min(98, max(20, base_score + score_adj))

    # ── Determine trade type for hold time ────────────────────────────────
    trade_type = 'continuation'
    if any(w in name.lower() for w in ['reversal','two-bar','wedge','final flag']):
        trade_type = 'reversal'
    elif any(w in name.lower() for w in ['breakout','inside','ii']):
        trade_type = 'breakout'
    elif 'trend from' in name.lower():
        trade_type = 'continuation'

    max_hold_bars = BROOKS_MAX_HOLD.get(trade_type, 8)

    # ── Parse entry/stop/target prices ────────────────────────────────────
    def extract_price(txt):
        nums = _re.findall(r'\d+\.?\d*', str(txt))
        if nums:
            # Find number closest to current price
            candidates = [float(x) for x in nums
                          if curr * 0.5 < float(x) < curr * 1.5]
            return candidates[0] if candidates else None
        return None

    entry_price = extract_price(entry_txt)
    stop_price  = extract_price(stop_txt)

    # Extract multiple targets
    all_targets = _re.findall(r'\d+\.?\d*', str(target_txt))
    target_prices = [float(x) for x in all_targets
                     if curr * 0.5 < float(x) < curr * 2.0]

    t1 = target_prices[0] if len(target_prices) > 0 else None
    t2 = target_prices[1] if len(target_prices) > 1 else None

    # Compute measured move target if not found
    if entry_price and stop_price and not t1:
        risk = abs(entry_price - stop_price)
        t1   = entry_price + risk * 2 if is_bull_signal else entry_price - risk * 2
        t2   = entry_price + risk * 3 if is_bull_signal else entry_price - risk * 3

    # ── R:R calculation ────────────────────────────────────────────────────
    rr_val  = None
    if entry_price and stop_price and t1:
        risk   = abs(entry_price - stop_price)
        reward = abs(t1 - entry_price)
        rr_val = reward / risk if risk > 0 else None

    # ── Failure signals (Brooks-specific) ─────────────────────────────────
    failure_signals = []
    if trade_type == 'reversal':
        failure_signals = [
            f"A large with-trend bar forms immediately after entry → exit at breakeven",
            f"Price doesn't reward within {max_hold_bars} bars → exit regardless",
            "Second reversal attempt also fails → strong trend, stop all countertrend trades",
            "Price closes beyond the stop level on a large trend bar → exit immediately",
        ]
    elif trade_type == 'breakout':
        failure_signals = [
            "Breakout bar immediately reverses and closes back inside the range",
            "Follow-through bar is weak (small body, opposite close) → danger sign",
            f"Price returns to breakout level within 3 bars → failed breakout",
            "Large opposing bar within 5 bars of entry → exit immediately",
        ]
    else:  # continuation
        failure_signals = [
            "Price breaks below the entry signal bar low without making progress",
            "A large counter-trend bar closes beyond 50% of the signal bar",
            "20 EMA turns flat or down during a bull signal → trend changing",
            f"No progress toward target within {max(max_hold_bars, 5)} bars → exit",
        ]

    # ── Scale-out plan ─────────────────────────────────────────────────────
    scale_plan = []
    if t1:
        scale_plan.append(f"At T1 ({t1:.2f}): Scale 50% — move stop to breakeven")
    if t2:
        scale_plan.append(f"At T2 ({t2:.2f}): Scale 30% — trail stop below swing lows")
    scale_plan.append("Runner (20%): Hold with trailing stop — let it run in strong trends")
    if trade_type == 'reversal':
        scale_plan.append(f"MAX HOLD: {max_hold_bars} bars — if no reward by then, exit all")

    # ── Position size rule ─────────────────────────────────────────────────
    direction_type = 'with-trend' if with_trend else \
                     'counter-trend' if counter_trend else trade_type
    size_rule = BROOKS_SIZE_RULES.get(direction_type,
                    BROOKS_SIZE_RULES.get(trade_type, 'STANDARD'))

    # ── Verdict ───────────────────────────────────────────────────────────
    if quality_score >= 80:
        verdict = '✅ HIGH QUALITY — TAKE THE TRADE'
        verdict_tag = 'good'
        verdict_detail = f"Strong confluence of context factors ({quality_score}/100). Full position size appropriate."
    elif quality_score >= 65:
        verdict = '⚠ MODERATE — TRADE WITH STANDARD SIZE'
        verdict_tag = 'warn'
        verdict_detail = f"Setup is valid ({quality_score}/100) but not perfect. Standard position. Tight stop."
    elif quality_score >= 50:
        verdict = '⚠ LOW QUALITY — REDUCE SIZE OR SKIP'
        verdict_tag = 'warn'
        verdict_detail = f"Only {quality_score}/100. Too many context factors against. Wait for better setup."
    else:
        verdict = '❌ SKIP — CONTEXT TOO POOR'
        verdict_tag = 'bad'
        verdict_detail = f"Quality score {quality_score}/100. Setup exists but conditions are unfavourable."

    # ── Brooks chapter reference ───────────────────────────────────────────
    db_entry = None
    for key in BROOKS_DB:
        if any(w.lower() in key.lower()
               for w in name.replace('Brooks: ', '').split()[:2]):
            db_entry = BROOKS_DB[key]
            break

    return {
        'name':           name,
        'signal':         signal,
        'source':         source,
        'icon':           icon,
        'curr':           curr,
        'ema20':          ema20,
        'adx':            adx,
        'trend_strength': trend_strength,
        'with_trend':     with_trend,
        'counter_trend':  counter_trend,
        'always_in':      'BULL' if always_in_bull else ('BEAR' if always_in_bear else 'NEUTRAL'),
        # Scores
        'base_score':     base_score,
        'score_adj':      score_adj,
        'quality_score':  quality_score,
        'context_items':  context_items,
        # Trade plan
        'entry_price':    entry_price,
        'stop_price':     stop_price,
        't1':             t1,
        't2':             t2,
        'rr_val':         rr_val,
        'trade_type':     trade_type,
        'max_hold_bars':  max_hold_bars,
        'scale_plan':     scale_plan,
        'size_rule':      size_rule,
        # Failure
        'failure_signals':failure_signals,
        # Verdict
        'verdict':        verdict,
        'verdict_tag':    verdict_tag,
        'verdict_detail': verdict_detail,
        # DB reference
        'db_entry':       db_entry,
        # Raw text
        'entry_txt':      entry_txt,
        'stop_txt':       stop_txt,
        'target_txt':     target_txt,
        'desc':           desc,
    }



# ─────────────────────────────────────────────────────────────────────────────
#  BACKTESTING ENGINE
#  Scans historical OHLC for past occurrences of each pattern type,
#  records actual outcomes (hit target / hit stop / timeout),
#  and computes win rate, avg gain/loss, and expectancy.
#  This converts theoretical patterns into tested, instrument-specific edge.
# ─────────────────────────────────────────────────────────────────────────────

def run_backtest(df, pattern_type, direction, confidence_threshold=60,
                 max_hold_days=30, progress_cb=None):
    """
    Scan full historical OHLC for occurrences of a pattern type.
    For each occurrence, simulate the trade and record outcome.

    Parameters:
        df                   : full OHLC DataFrame
        pattern_type         : pattern name string (e.g. 'Double Bottom')
        direction            : 'BULLISH' or 'BEARISH'
        confidence_threshold : minimum confidence to count (default 60)
        max_hold_days        : exit after N bars if neither target nor stop hit
        progress_cb          : optional callback(pct) for progress bar

    Returns list of trade dicts with full outcome data.
    """
    trades = []
    n = len(df)
    if n < 60:
        return trades

    closes = df['Close'].values
    highs  = df['High'].values
    lows   = df['Low'].values

    # ── Sliding window scan ───────────────────────────────────────────────
    # Use 60-bar windows, stepping every 5 bars for speed
    min_window = 40
    step       = 3
    windows    = range(min_window, n - max_hold_days - 5, step)
    total_w    = len(windows)

    for wi, end_idx in enumerate(windows):
        if progress_cb and wi % 20 == 0:
            progress_cb(int(wi / total_w * 100))

        # Slice window
        window_df = df.iloc[:end_idx].copy()
        window_df.reset_index(drop=True, inplace=True)

        # Run pattern detection on this window
        try:
            pats = detect_patterns(window_df)
        except Exception:
            continue

        for pat in pats:
            # Filter: must match requested pattern type and direction
            if pattern_type.lower() not in pat['name'].lower():
                continue
            if direction not in pat.get('direction', ''):
                continue
            if pat.get('confidence', 0) < confidence_threshold:
                continue

            # ── Get trade parameters ──────────────────────────────────────
            neckline = pat.get('neckline')
            pat_low  = pat.get('pattern_low')
            pat_high = pat.get('pattern_high')

            # Parse entry, stop, target from strings
            import re as _re
            def extract_price(txt, curr_price):
                nums = _re.findall(r'\d+\.?\d*', str(txt))
                candidates = [float(x) for x in nums
                              if curr_price * 0.3 < float(x) < curr_price * 3]
                return candidates[0] if candidates else None

            curr_p = closes[end_idx - 1]
            entry  = extract_price(pat.get('entry', ''), curr_p)
            stop   = extract_price(pat.get('stop', ''),  curr_p)
            target = extract_price(pat.get('target', ''),curr_p)

            if not entry or not stop or not target:
                continue
            if entry <= 0 or stop <= 0 or target <= 0:
                continue

            risk   = abs(entry - stop)
            reward = abs(target - entry)
            if risk <= 0:
                continue
            rr = reward / risk

            # ── Simulate the trade forward ────────────────────────────────
            entry_bar = end_idx
            outcome   = 'TIMEOUT'
            exit_price= curr_p
            exit_bar  = min(entry_bar + max_hold_days, n - 1)
            bars_held  = 0

            for fwd in range(entry_bar, min(entry_bar + max_hold_days, n)):
                bars_held = fwd - entry_bar + 1
                bar_h = highs[fwd]
                bar_l = lows[fwd]
                bar_c = closes[fwd]

                if direction == 'BULLISH':
                    # Entry: price breaks above neckline/entry
                    if bar_h >= entry:
                        # Check stop first (worst case within same bar)
                        if bar_l <= stop:
                            outcome    = 'STOP'
                            exit_price = stop
                            exit_bar   = fwd
                            break
                        # Check target
                        if bar_h >= target:
                            outcome    = 'TARGET'
                            exit_price = target
                            exit_bar   = fwd
                            break
                else:  # BEARISH
                    if bar_l <= entry:
                        if bar_h >= stop:
                            outcome    = 'STOP'
                            exit_price = stop
                            exit_bar   = fwd
                            break
                        if bar_l <= target:
                            outcome    = 'TARGET'
                            exit_price = target
                            exit_bar   = fwd
                            break

            # ── Compute P&L ────────────────────────────────────────────────
            if direction == 'BULLISH':
                pnl_pct = (exit_price - entry) / entry * 100
            else:
                pnl_pct = (entry - exit_price) / entry * 100

            # Get entry date for reference
            entry_date = str(df['Date'].iloc[entry_bar])[:10] \
                         if 'Date' in df.columns else str(entry_bar)

            # Avoid duplicate detections (same pattern, close bars)
            duplicate = False
            for prev in trades[-5:]:
                if abs(prev['entry_bar'] - entry_bar) < 15:
                    duplicate = True
                    break
            if duplicate:
                continue

            trades.append({
                'entry_date':  entry_date,
                'entry_bar':   entry_bar,
                'exit_bar':    exit_bar,
                'bars_held':   bars_held,
                'pattern':     pat['name'],
                'direction':   direction,
                'confidence':  pat.get('confidence', 0),
                'entry_price': round(entry, 2),
                'stop_price':  round(stop, 2),
                'target_price':round(target, 2),
                'exit_price':  round(exit_price, 2),
                'rr_setup':    round(rr, 2),
                'outcome':     outcome,
                'pnl_pct':     round(pnl_pct, 2),
                'hit_target':  outcome == 'TARGET',
                'hit_stop':    outcome == 'STOP',
                'timeout':     outcome == 'TIMEOUT',
            })

    if progress_cb:
        progress_cb(100)

    return trades


def compute_backtest_stats(trades):
    """Compute summary statistics from a list of backtest trades."""
    if not trades:
        return None

    total   = len(trades)
    wins    = [t for t in trades if t['hit_target']]
    losses  = [t for t in trades if t['hit_stop']]
    timeouts= [t for t in trades if t['timeout']]

    win_rate  = len(wins) / total * 100 if total > 0 else 0
    avg_win   = np.mean([t['pnl_pct'] for t in wins])   if wins    else 0
    avg_loss  = np.mean([t['pnl_pct'] for t in losses]) if losses  else 0
    avg_to    = np.mean([t['pnl_pct'] for t in timeouts])if timeouts else 0
    avg_hold  = np.mean([t['bars_held'] for t in trades])

    # Expectancy = (Win% × avg_win) + (Loss% × avg_loss)
    loss_rate  = len(losses)  / total * 100
    to_rate    = len(timeouts)/ total * 100
    expectancy = (win_rate/100 * avg_win +
                  loss_rate/100 * avg_loss +
                  to_rate/100 * avg_to)

    # Profit factor
    gross_profit = sum(t['pnl_pct'] for t in wins)
    gross_loss   = abs(sum(t['pnl_pct'] for t in losses))
    profit_factor= gross_profit / gross_loss if gross_loss > 0 else float('inf')

    # Grade
    if win_rate >= 65 and expectancy >= 3:
        grade = 'A+ — EXCELLENT EDGE'
    elif win_rate >= 55 and expectancy >= 1:
        grade = 'A  — GOOD EDGE'
    elif win_rate >= 50 and expectancy >= 0:
        grade = 'B  — MARGINAL EDGE'
    elif expectancy >= 0:
        grade = 'C  — WEAK POSITIVE'
    else:
        grade = 'D  — NEGATIVE EXPECTANCY'

    return {
        'total':          total,
        'wins':           len(wins),
        'losses':         len(losses),
        'timeouts':       len(timeouts),
        'win_rate':       round(win_rate, 1),
        'loss_rate':      round(loss_rate, 1),
        'timeout_rate':   round(to_rate, 1),
        'avg_win':        round(avg_win, 2),
        'avg_loss':       round(avg_loss, 2),
        'avg_timeout':    round(avg_to, 2),
        'expectancy':     round(expectancy, 2),
        'profit_factor':  round(profit_factor, 2),
        'avg_hold_bars':  round(avg_hold, 1),
        'grade':          grade,
        'trades':         trades,
    }


def detect_patterns(df):
    """
    Detect chart patterns from OHLCV dataframe.
    Returns list of dicts: {pattern_name, confidence, details, bar_indices}
    """
    detected = []
    n = len(df)
    if n < 20:
        return detected

    highs_idx, lows_idx = find_swing_highs_lows(df, order=max(3, n//15))
    closes = df['Close'].values
    highs  = df['High'].values
    lows   = df['Low'].values

    # ── HELPER: latest N swing lows/highs ──
    def last_n_lows(n_pts):
        return [(lows_idx[i], lows[lows_idx[i]]) for i in range(-n_pts, 0)] if len(lows_idx) >= n_pts else []

    def last_n_highs(n_pts):
        return [(highs_idx[i], highs[highs_idx[i]]) for i in range(-n_pts, 0)] if len(highs_idx) >= n_pts else []

    # ──────────────────────────────────────────────────────
    # 1. DOUBLE BOTTOM Detection
    # ──────────────────────────────────────────────────────
    if len(lows_idx) >= 2:
        pts = last_n_lows(2)
        if len(pts) == 2:
            idx1, v1 = pts[0]
            idx2, v2 = pts[1]
            price_diff = pct_diff(v1, v2)
            if price_diff <= 4.0 and (idx2 - idx1) >= 5:
                # Find peak between the two lows
                between_highs = highs[idx1:idx2+1]
                peak_val = between_highs.max() if len(between_highs) > 0 else 0
                neckline_rise = (peak_val - min(v1, v2)) / min(v1, v2) * 100
                if neckline_rise >= 8:
                    # Classify Adam vs Eve
                    # Simple heuristic: if low spans few bars = Adam (sharp); many bars = Eve (wide)
                    # Use range of the bottom (distance around the low point)
                    span1 = 1
                    for k in range(min(idx1, n-1), min(idx1+4, n)):
                        if lows[k] > v1 * 1.02: break
                        span1 += 1
                    span2 = 1
                    for k in range(min(idx2, n-1), min(idx2+4, n)):
                        if lows[k] > v2 * 1.02: break
                        span2 += 1
                    t1 = "Adam" if span1 <= 2 else "Eve"
                    t2 = "Adam" if span2 <= 2 else "Eve"
                    pattern_name = f"Double Bottom ({t1} & {t2})"
                    conf = 85 - price_diff * 3
                    conf = max(40, min(95, conf))
                    current_price = closes[-1]
                    neckline_price = peak_val
                    pattern_height = neckline_price - min(v1, v2)
                    target = neckline_price + pattern_height
                    stop   = min(v1, v2) * 0.99
                    detected.append({
                        "name": pattern_name,
                        "confidence": round(conf, 1),
                        "direction": "BULLISH",
                        "entry": f"Close above neckline: {neckline_price:.2f}",
                        "stop":   f"{stop:.2f} (below lower bottom)",
                        "target": f"{target:.2f} (pattern height projection)",
                        "details": f"Bottom 1: {v1:.2f} at bar {idx1}, Bottom 2: {v2:.2f} at bar {idx2}, Price diff: {price_diff:.1f}%, Neckline: {neckline_price:.2f}",
                        "bar_indices": [idx1, idx2],
                        "neckline": neckline_price,
                        "pattern_low": min(v1, v2),
                    })

    # ──────────────────────────────────────────────────────
    # 2. DOUBLE TOP Detection
    # ──────────────────────────────────────────────────────
    if len(highs_idx) >= 2:
        pts = last_n_highs(2)
        if len(pts) == 2:
            idx1, v1 = pts[0]
            idx2, v2 = pts[1]
            price_diff = pct_diff(v1, v2)
            if price_diff <= 4.0 and (idx2 - idx1) >= 5:
                between_lows = lows[idx1:idx2+1]
                valley_val = between_lows.min() if len(between_lows) > 0 else 0
                valley_drop = (max(v1, v2) - valley_val) / max(v1, v2) * 100
                if valley_drop >= 8:
                    span1 = 1
                    for k in range(min(idx1, n-1), min(idx1+4, n)):
                        if highs[k] < v1 * 0.98: break
                        span1 += 1
                    span2 = 1
                    for k in range(min(idx2, n-1), min(idx2+4, n)):
                        if highs[k] < v2 * 0.98: break
                        span2 += 1
                    t1 = "Adam" if span1 <= 2 else "Eve"
                    t2 = "Adam" if span2 <= 2 else "Eve"
                    pattern_name = f"Double Top ({t1} & {t2})"
                    conf = 82 - price_diff * 3
                    conf = max(40, min(93, conf))
                    neckline_price = valley_val
                    pattern_height = max(v1, v2) - neckline_price
                    target = neckline_price - pattern_height
                    stop   = max(v1, v2) * 1.01
                    detected.append({
                        "name": pattern_name,
                        "confidence": round(conf, 1),
                        "direction": "BEARISH",
                        "entry": f"Close below neckline: {neckline_price:.2f}",
                        "stop":   f"{stop:.2f} (above higher top)",
                        "target": f"{target:.2f} (pattern height projection)",
                        "details": f"Top 1: {v1:.2f} at bar {idx1}, Top 2: {v2:.2f} at bar {idx2}, Price diff: {price_diff:.1f}%, Neckline: {neckline_price:.2f}",
                        "bar_indices": [idx1, idx2],
                        "neckline": neckline_price,
                        "pattern_high": max(v1, v2),
                    })

    # ──────────────────────────────────────────────────────
    # 3. HEAD AND SHOULDERS TOP
    # ──────────────────────────────────────────────────────
    if len(highs_idx) >= 3:
        pts = last_n_highs(3)
        if len(pts) == 3:
            (i1, h1), (i2, h2), (i3, h3) = pts
            # Head must be higher than both shoulders
            if h2 > h1 and h2 > h3:
                shoulder_diff = pct_diff(h1, h3)
                if shoulder_diff <= 7 and (i2 - i1) >= 3 and (i3 - i2) >= 3:
                    # Find neckline: lows between shoulders
                    between1 = lows[i1:i2+1].min()
                    between2 = lows[i2:i3+1].min()
                    neckline  = min(between1, between2)
                    head_height = h2 - neckline
                    target = neckline - head_height
                    stop   = h3 * 1.005
                    conf = 80 - shoulder_diff * 2
                    conf = max(45, min(92, conf))
                    detected.append({
                        "name": "Head-and-Shoulders Top",
                        "confidence": round(conf, 1),
                        "direction": "BEARISH",
                        "entry": f"Close below neckline: {neckline:.2f}",
                        "stop":   f"{stop:.2f} (above right shoulder)",
                        "target": f"{target:.2f} (head-to-neckline projected down)",
                        "details": f"Left shoulder: {h1:.2f}, Head: {h2:.2f}, Right shoulder: {h3:.2f}, Neckline: {neckline:.2f}, Shoulder diff: {shoulder_diff:.1f}%",
                        "bar_indices": [i1, i2, i3],
                        "neckline": neckline,
                        "pattern_high": h2,
                    })

    # ──────────────────────────────────────────────────────
    # 4. HEAD AND SHOULDERS BOTTOM (Inverse H&S)
    # ──────────────────────────────────────────────────────
    if len(lows_idx) >= 3:
        pts = last_n_lows(3)
        if len(pts) == 3:
            (i1, l1), (i2, l2), (i3, l3) = pts
            if l2 < l1 and l2 < l3:
                shoulder_diff = pct_diff(l1, l3)
                if shoulder_diff <= 7 and (i2 - i1) >= 3 and (i3 - i2) >= 3:
                    between1 = highs[i1:i2+1].max()
                    between2 = highs[i2:i3+1].max()
                    neckline  = max(between1, between2)
                    head_depth = neckline - l2
                    target = neckline + head_depth
                    stop   = l3 * 0.995
                    conf = 80 - shoulder_diff * 2
                    conf = max(45, min(92, conf))
                    detected.append({
                        "name": "Head-and-Shoulders Bottom",
                        "confidence": round(conf, 1),
                        "direction": "BULLISH",
                        "entry": f"Close above neckline: {neckline:.2f}",
                        "stop":   f"{stop:.2f} (below right shoulder)",
                        "target": f"{target:.2f} (head-to-neckline projected up)",
                        "details": f"Left shoulder: {l1:.2f}, Head: {l2:.2f}, Right shoulder: {l3:.2f}, Neckline: {neckline:.2f}, Shoulder diff: {shoulder_diff:.1f}%",
                        "bar_indices": [i1, i2, i3],
                        "neckline": neckline,
                        "pattern_low": l2,
                    })

    # ──────────────────────────────────────────────────────
    # 5. ASCENDING TRIANGLE
    # ──────────────────────────────────────────────────────
    if len(highs_idx) >= 2 and len(lows_idx) >= 2:
        recent_highs_vals = [highs[i] for i in highs_idx[-4:]]
        recent_lows_idx   = lows_idx[-4:]
        recent_lows_vals  = [lows[i] for i in recent_lows_idx]
        if len(recent_highs_vals) >= 2 and len(recent_lows_vals) >= 2:
            flat_top = max(pct_diff(recent_highs_vals[i], recent_highs_vals[i+1]) for i in range(len(recent_highs_vals)-1)) < 3
            rising_bottom = all(recent_lows_vals[i] < recent_lows_vals[i+1] for i in range(len(recent_lows_vals)-1))
            if flat_top and rising_bottom:
                resistance = np.mean(recent_highs_vals)
                pattern_low = min(recent_lows_vals)
                height = resistance - pattern_low
                target = resistance + height
                stop   = min(recent_lows_vals[-2:]) * 0.99
                detected.append({
                    "name": "Ascending Triangle",
                    "confidence": 72.0,
                    "direction": "BULLISH (70% breakout upward)",
                    "entry": f"Close above flat resistance: {resistance:.2f}",
                    "stop":   f"{stop:.2f} (below recent higher low)",
                    "target": f"{target:.2f} (triangle height added to breakout)",
                    "details": f"Flat resistance at ~{resistance:.2f}, Rising lows from {pattern_low:.2f}",
                    "bar_indices": list(highs_idx[-3:]) + list(lows_idx[-3:]),
                    "neckline": resistance,
                    "pattern_low": pattern_low,
                })

    # ──────────────────────────────────────────────────────
    # 6. DESCENDING TRIANGLE
    # ──────────────────────────────────────────────────────
    if len(highs_idx) >= 2 and len(lows_idx) >= 2:
        recent_lows_vals  = [lows[i] for i in lows_idx[-4:]]
        recent_highs_vals = [highs[i] for i in highs_idx[-4:]]
        if len(recent_lows_vals) >= 2 and len(recent_highs_vals) >= 2:
            flat_bottom   = max(pct_diff(recent_lows_vals[i], recent_lows_vals[i+1]) for i in range(len(recent_lows_vals)-1)) < 3
            falling_top   = all(recent_highs_vals[i] > recent_highs_vals[i+1] for i in range(len(recent_highs_vals)-1))
            if flat_bottom and falling_top:
                support = np.mean(recent_lows_vals)
                pattern_high = max(recent_highs_vals)
                height = pattern_high - support
                target = support - height
                stop   = max(recent_highs_vals[-2:]) * 1.01
                detected.append({
                    "name": "Descending Triangle",
                    "confidence": 68.0,
                    "direction": "BEARISH (64% breakout downward)",
                    "entry": f"Close below flat support: {support:.2f}",
                    "stop":   f"{stop:.2f} (above recent lower high)",
                    "target": f"{target:.2f} (triangle height subtracted from breakout)",
                    "details": f"Flat support at ~{support:.2f}, Falling highs from {pattern_high:.2f}",
                    "bar_indices": list(lows_idx[-3:]) + list(highs_idx[-3:]),
                    "neckline": support,
                    "pattern_high": pattern_high,
                })

    # ──────────────────────────────────────────────────────
    # 7. SYMMETRICAL TRIANGLE
    # ──────────────────────────────────────────────────────
    if len(highs_idx) >= 2 and len(lows_idx) >= 2:
        rh = [highs[i] for i in highs_idx[-4:]]
        rl = [lows[i] for i in lows_idx[-4:]]
        if len(rh) >= 2 and len(rl) >= 2:
            falling_top  = all(rh[i] > rh[i+1] for i in range(len(rh)-1))
            rising_bottom = all(rl[i] < rl[i+1] for i in range(len(rl)-1))
            if falling_top and rising_bottom:
                upper_val = rh[-1]
                lower_val = rl[-1]
                apex_est = (upper_val + lower_val) / 2
                height = max(rh) - min(rl)
                # Determine likely direction from prior trend
                prior_trend_up = closes[max(0, n-20)] < closes[-1]
                direction = "BULLISH (prior uptrend)" if prior_trend_up else "BEARISH (prior downtrend)"
                target_up = upper_val + height * 0.6
                target_dn = lower_val - height * 0.6
                detected.append({
                    "name": "Symmetrical Triangle",
                    "confidence": 65.0,
                    "direction": direction,
                    "entry": f"Close above {upper_val:.2f} (upward) OR below {lower_val:.2f} (downward)",
                    "stop":   f"Inside the triangle (opposite trendline)",
                    "target": f"Up: {target_up:.2f} | Down: {target_dn:.2f} (triangle height from breakout)",
                    "details": f"Upper trendline falling from {max(rh):.2f} to {rh[-1]:.2f}, Lower trendline rising from {min(rl):.2f} to {rl[-1]:.2f}",
                    "bar_indices": list(highs_idx[-3:]) + list(lows_idx[-3:]),
                    "neckline": upper_val,
                    "pattern_low": lower_val,
                })

    # ──────────────────────────────────────────────────────
    # 8. CUP WITH HANDLE (Simple detection)
    # ──────────────────────────────────────────────────────
    if n >= 40:
        # Look for: prior high → decline → U-shape → recovery → small pullback → breakout
        window = closes[-40:]
        peak1 = window[:10].max()
        cup_low = window[5:30].min()
        cup_low_idx = window[5:30].argmin() + 5
        peak2 = window[25:35].max()
        handle_low = window[30:].min()
        peak1_idx_a = window[:10].argmax()
        # Cup depth check: 15-50%
        cup_depth_pct = (peak1 - cup_low) / peak1 * 100
        # Recovery check: peak2 close to peak1
        recovery_pct = pct_diff(peak1, peak2)
        handle_depth = (peak2 - handle_low) / peak2 * 100
        if (15 <= cup_depth_pct <= 60 and
            recovery_pct <= 8 and
            5 <= handle_depth <= 25 and
            cup_low_idx >= 5):
            target = peak2 + (peak2 - cup_low)  # Cup depth projected
            stop   = handle_low * 0.99
            conf = max(55, min(85, 80 - recovery_pct * 3 - abs(cup_depth_pct - 30) * 0.5))
            detected.append({
                "name": "Cup with Handle",
                "confidence": round(conf, 1),
                "direction": "BULLISH",
                "entry": f"Close above cup rim/lip: ~{peak2:.2f}",
                "stop":   f"{stop:.2f} (below handle low)",
                "target": f"{target:.2f} (cup depth projected from rim)",
                "details": f"Cup high: ~{peak1:.2f}, Cup low: ~{cup_low:.2f}, Depth: {cup_depth_pct:.1f}%, Handle drop: {handle_depth:.1f}%",
                "bar_indices": [max(0, n-40), max(0, n-40)+cup_low_idx, n-1],
                "neckline": peak2,
                "pattern_low": cup_low,
            })

    # ──────────────────────────────────────────────────────
    # 9. FLAG PATTERN (Bull)
    # ──────────────────────────────────────────────────────
    if n >= 20:
        pole_start = n - 20
        pole_end   = n - 10
        flag_start = n - 10

        pole_rise = (closes[pole_end-1] - closes[pole_start]) / closes[pole_start] * 100
        flag_high = highs[flag_start:].max()
        flag_low  = lows[flag_start:].min()
        flag_drop = (flag_high - flag_low) / flag_high * 100
        pole_height = closes[pole_end-1] - closes[pole_start]

        if pole_rise >= 8 and flag_drop <= 12:
            # Is the flag slightly declining?
            flag_closes = closes[flag_start:]
            if len(flag_closes) >= 3:
                flag_slope = np.polyfit(range(len(flag_closes)), flag_closes, 1)[0]
                if flag_slope < 0:  # Declining flag (correct)
                    target = flag_high + pole_height
                    stop   = flag_low * 0.99
                    conf = max(55, min(85, 75 + pole_rise * 0.3 - flag_drop))
                    detected.append({
                        "name": "Flag (Bull)",
                        "confidence": round(conf, 1),
                        "direction": "BULLISH",
                        "entry": f"Close above flag top: ~{flag_high:.2f}",
                        "stop":   f"{stop:.2f} (below flag low)",
                        "target": f"{target:.2f} (flagpole height added to flag low)",
                        "details": f"Pole rise: {pole_rise:.1f}%, Flag range: {flag_drop:.1f}%, Pole height: {pole_height:.2f}",
                        "bar_indices": [pole_start, pole_end, flag_start, n-1],
                        "neckline": flag_high,
                        "pattern_low": flag_low,
                    })

    # ──────────────────────────────────────────────────────
    # 10. TRIPLE BOTTOM
    # ──────────────────────────────────────────────────────
    if len(lows_idx) >= 3:
        pts = last_n_lows(3)
        if len(pts) == 3:
            (i1, l1), (i2, l2), (i3, l3) = pts
            max_diff = max(pct_diff(l1, l2), pct_diff(l2, l3), pct_diff(l1, l3))
            if max_diff <= 3 and (i2 - i1) >= 4 and (i3 - i2) >= 4:
                neckline = highs[i1:i3+1].max()
                pattern_height = neckline - min(l1, l2, l3)
                target = neckline + pattern_height
                stop   = min(l1, l2, l3) * 0.99
                conf = 85 - max_diff * 5
                conf = max(50, min(92, conf))
                detected.append({
                    "name": "Triple Bottom",
                    "confidence": round(conf, 1),
                    "direction": "BULLISH",
                    "entry": f"Close above neckline: {neckline:.2f}",
                    "stop":   f"{stop:.2f} (below lowest bottom)",
                    "target": f"{target:.2f} (pattern height added to neckline)",
                    "details": f"Three lows: {l1:.2f}, {l2:.2f}, {l3:.2f}. Max price diff: {max_diff:.1f}%. Neckline: {neckline:.2f}",
                    "bar_indices": [i1, i2, i3],
                    "neckline": neckline,
                    "pattern_low": min(l1, l2, l3),
                })

    # ──────────────────────────────────────────────────────
    # 11. TRIPLE TOP
    # ──────────────────────────────────────────────────────
    if len(highs_idx) >= 3:
        pts = last_n_highs(3)
        if len(pts) == 3:
            (i1, h1), (i2, h2), (i3, h3) = pts
            max_diff = max(pct_diff(h1, h2), pct_diff(h2, h3), pct_diff(h1, h3))
            if max_diff <= 3 and (i2 - i1) >= 4 and (i3 - i2) >= 4:
                neckline = lows[i1:i3+1].min()
                pattern_height = max(h1, h2, h3) - neckline
                target = neckline - pattern_height
                stop   = max(h1, h2, h3) * 1.01
                conf = 85 - max_diff * 5
                conf = max(50, min(92, conf))
                detected.append({
                    "name": "Triple Top",
                    "confidence": round(conf, 1),
                    "direction": "BEARISH",
                    "entry": f"Close below neckline: {neckline:.2f}",
                    "stop":   f"{stop:.2f} (above highest top)",
                    "target": f"{target:.2f} (pattern height subtracted from neckline)",
                    "details": f"Three highs: {h1:.2f}, {h2:.2f}, {h3:.2f}. Max price diff: {max_diff:.1f}%. Neckline: {neckline:.2f}",
                    "bar_indices": [i1, i2, i3],
                    "neckline": neckline,
                    "pattern_high": max(h1, h2, h3),
                })

    # ──────────────────────────────────────────────────────
    # 12. MEASURED MOVE UP / DOWN
    # ──────────────────────────────────────────────────────
    if len(highs_idx) >= 2 and len(lows_idx) >= 2:
        # Look for: swing low → swing high → correction low → potential leg 2
        if len(lows_idx) >= 2 and len(highs_idx) >= 1:
            l_start_idx = lows_idx[-2] if len(lows_idx) >= 2 else lows_idx[-1]
            h_peak_idx  = highs_idx[-1]
            l_corr_idx  = lows_idx[-1]

            if l_start_idx < h_peak_idx > l_corr_idx:
                leg1 = highs[h_peak_idx] - lows[l_start_idx]
                corr = (highs[h_peak_idx] - lows[l_corr_idx]) / highs[h_peak_idx] * 100
                if 25 <= corr <= 65 and leg1 > 0:
                    target = lows[l_corr_idx] + leg1
                    stop   = lows[l_corr_idx] * 0.99
                    detected.append({
                        "name": "Measured Move Up",
                        "confidence": 70.0,
                        "direction": "BULLISH",
                        "entry": f"Enter as Leg 2 begins. Buy around correction low: {lows[l_corr_idx]:.2f}",
                        "stop":   f"{stop:.2f} (below correction low)",
                        "target": f"{target:.2f} (Leg 1 distance = Leg 2 distance: {leg1:.2f} pts)",
                        "details": f"Leg 1: {lows[l_start_idx]:.2f} → {highs[h_peak_idx]:.2f} ({leg1:.2f} pts). Correction: {corr:.1f}%. Target: correction low + {leg1:.2f}",
                        "bar_indices": [l_start_idx, h_peak_idx, l_corr_idx],
                        "neckline": highs[h_peak_idx],
                        "pattern_low": lows[l_corr_idx],
                    })

    # Sort by confidence
    detected.sort(key=lambda x: x['confidence'], reverse=True)

    # Add completion status to every pattern
    for p in detected:
        p['completion'] = get_completion_status(p, df)

    return detected


# ─────────────────────────────────────────────────────────────────────────────
#  CHART DRAWING
# ─────────────────────────────────────────────────────────────────────────────

def draw_chart(fig, df, detected_patterns):
    """Draw OHLCV chart with detected pattern annotations and completion status."""
    fig.clear()
    ax = fig.add_subplot(111)
    ax.set_facecolor('#ffffff')
    fig.patch.set_facecolor('#f8f9fa')

    dates = range(len(df))
    o = df['Open'].values
    h = df['High'].values
    l = df['Low'].values
    c = df['Close'].values

    # Draw candlesticks
    width = 0.6
    for i in dates:
        color = '#2ecc71' if c[i] >= o[i] else '#e74c3c'
        ax.plot([i, i], [l[i], h[i]], color=color, linewidth=0.8, zorder=2)
        body_lo = min(o[i], c[i])
        body_hi = max(o[i], c[i])
        rect = plt.Rectangle((i - width/2, body_lo), width, body_hi - body_lo,
                              facecolor=color, edgecolor=color, zorder=3)
        ax.add_patch(rect)

    # Annotate detected patterns
    colors_cycle = ['#f1c40f', '#3498db', '#e67e22', '#9b59b6', '#1abc9c']
    for pi, pat in enumerate(detected_patterns[:3]):
        comp = pat.get('completion', {})
        # Use completion color if available, else cycle color
        col  = comp.get('color', colors_cycle[pi % len(colors_cycle)])

        # Highlight bar indices
        for bi in pat.get('bar_indices', []):
            if 0 <= bi < len(df):
                ax.axvline(x=bi, color=col, linestyle='--', alpha=0.4, linewidth=1)

        # Draw neckline
        if 'neckline' in pat:
            status_txt = comp.get('status', '')
            lbl = f"{pat['name'][:18]}: {pat['neckline']:.2f}  {status_txt}"
            ax.axhline(y=pat['neckline'], color=col, linestyle='-',
                       alpha=0.85, linewidth=1.5, label=lbl)

        # Draw stop line
        if 'pattern_low' in pat:
            ax.axhline(y=pat['pattern_low'], color='#e74c3c',
                       linestyle=':', alpha=0.5, linewidth=1,
                       label=f"Stop: {pat['pattern_low']:.2f}")
        if 'pattern_high' in pat:
            ax.axhline(y=pat['pattern_high'], color='#e74c3c',
                       linestyle=':', alpha=0.5, linewidth=1,
                       label=f"Stop: {pat['pattern_high']:.2f}")

        # Draw target line if parseable
        try:
            import re
            nums = re.findall(r'\d+\.?\d*', str(pat.get('target', '')))
            if nums:
                tgt = float(nums[0])
                ax.axhline(y=tgt, color='#2ecc71', linestyle='-.',
                           alpha=0.5, linewidth=1,
                           label=f"Target: {tgt:.2f}")
        except Exception:
            pass

        # Shade the pattern region
        indices = pat.get('bar_indices', [])
        if len(indices) >= 2:
            x_start = max(0, min(indices) - 2)
            x_end   = min(len(df) - 1, max(indices) + 2)
            ax.axvspan(x_start, x_end, alpha=0.06, color=col, zorder=1)

    # ── COMPLETION STATUS BADGE (top-left of chart) ────────────────────────
    if detected_patterns:
        top_pat  = detected_patterns[0]
        comp     = top_pat.get('completion', {})
        status   = comp.get('status', '')
        pct      = comp.get('pct', 0)
        if status:
            badge_color = comp.get('color', '#f1c40f')
            ax.text(0.01, 0.97,
                    f"{status}  ({pct}% complete)",
                    transform=ax.transAxes,
                    color=badge_color, fontsize=8,
                    verticalalignment='top',
                    bbox=dict(boxstyle='round,pad=0.3',
                              facecolor='#fffef0',
                              edgecolor=badge_color,
                              alpha=0.85))

    # Styling
    ax.set_title('Chart Analysis — Bulkowski Pattern Detector',
                 color='#1a1d23', fontsize=11, pad=8)
    ax.tick_params(colors='#444444', labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor('#cccccc')

    date_labels = df['Date'].astype(str).values if 'Date' in df.columns else [str(i) for i in dates]
    step = max(1, len(dates) // 10)
    ax.set_xticks(list(dates)[::step])
    ax.set_xticklabels([date_labels[i][:10] for i in range(0, len(dates), step)],
                       rotation=30, ha='right', fontsize=7, color='#555')
    ax.set_ylabel('Price', color='#444', fontsize=9)

    if detected_patterns:
        ax.legend(loc='upper right', fontsize=7, facecolor='#ffffff',
                  labelcolor='#1a1d23', framealpha=0.8, edgecolor='#555',
                  ncol=1)

    try:
        fig.tight_layout(pad=0.5)
    except Exception:
        pass


def draw_chart_unified(fig, df, bulkowski_pats, quant_sigs, brooks_sigs,
                       street_smarts_sigs=None):
    """
    Unified chart drawing function.
    Draws all three signal categories on one candlestick chart with
    distinct colors and labels for each category.

    Color scheme:
      Bulkowski patterns  → GOLD  (#f1c40f)  solid lines
      Brooks PA signals   → TEAL  (#1abc9c)  dashed lines
      Quant signals       → BLUE  (#3498db)  dotted lines
      Stop levels         → RED   (#e74c3c)  dotted lines
      Target levels       → GREEN (#2ecc71)  dash-dot lines
    """
    import re as _re
    fig.clear()
    ax = fig.add_subplot(111)
    ax.set_facecolor('#ffffff')
    fig.patch.set_facecolor('#f8f9fa')

    n     = len(df)
    dates = range(n)
    o = df['Open'].values
    h = df['High'].values
    l = df['Low'].values
    c = df['Close'].values

    # ── Candlesticks ─────────────────────────────────────────────────────
    width = 0.6
    for i in dates:
        color = '#2ecc71' if c[i] >= o[i] else '#e74c3c'
        ax.plot([i, i], [l[i], h[i]], color=color, linewidth=0.8, zorder=2)
        body_lo = min(o[i], c[i])
        body_hi = max(o[i], c[i])
        if body_hi - body_lo < 0.01:
            body_hi = body_lo + 0.01
        rect = plt.Rectangle((i - width/2, body_lo), width, body_hi - body_lo,
                              facecolor=color, edgecolor=color, zorder=3)
        ax.add_patch(rect)

    legend_items = []

    # ── BULKOWSKI PATTERNS — Gold solid lines ─────────────────────────────
    BK_COL = '#f1c40f'
    for pi, pat in enumerate(bulkowski_pats[:2]):
        comp   = pat.get('completion', {})
        status = comp.get('status', '')

        # Neckline
        if 'neckline' in pat:
            nl = pat['neckline']
            lbl = f"[BK] {pat['name'][:16]}: {nl:.0f}"
            ln, = ax.plot([0, n-1], [nl, nl],
                          color=BK_COL, linestyle='-',
                          linewidth=1.8, alpha=0.9, zorder=5)
            ax.text(n * 0.01, nl, f" {lbl}", color=BK_COL,
                    fontsize=7, va='bottom', fontfamily='monospace',
                    bbox=dict(facecolor='#fffff0', edgecolor=BK_COL,
                              alpha=0.8, pad=1))
            legend_items.append((ln, lbl))

        # Stop
        stop_val = pat.get('pattern_low') or pat.get('pattern_high')
        if stop_val:
            ax.plot([0, n-1], [stop_val, stop_val],
                    color='#e74c3c', linestyle=':', linewidth=1.2, alpha=0.7, zorder=4)
            ax.text(n * 0.01, stop_val, f" Stop: {stop_val:.0f}",
                    color='#e74c3c', fontsize=6.5, va='bottom',
                    fontfamily='monospace')

        # Target
        try:
            nums = _re.findall(r'\d+\.?\d*', str(pat.get('target', '')))
            if nums:
                tgt = float(nums[0])
                ax.plot([0, n-1], [tgt, tgt],
                        color='#2ecc71', linestyle='-.', linewidth=1.2, alpha=0.7, zorder=4)
                ax.text(n * 0.01, tgt, f" Target: {tgt:.0f}",
                        color='#2ecc71', fontsize=6.5, va='bottom',
                        fontfamily='monospace')
        except Exception:
            pass

        # Shade pattern region
        indices = pat.get('bar_indices', [])
        if len(indices) >= 2:
            x0 = max(0, min(indices) - 2)
            x1 = min(n - 1, max(indices) + 2)
            ax.axvspan(x0, x1, alpha=0.07, color=BK_COL, zorder=1)

        # ── PATTERN POINT OVERLAY ──────────────────────────────────────
        # Draw the actual detected price points as dots + connecting lines
        # so user can see exactly where the pattern was found on the chart
        try:
            pat_name = pat.get('name', '').lower()
            pts_x = []; pts_y = []

            if indices and len(indices) >= 2:
                # Get actual price values at detected bar indices
                for idx in indices:
                    if 0 <= idx < n:
                        # For bullish: use lows, for bearish: use highs
                        if 'BULL' in pat.get('direction','').upper():
                            pts_x.append(idx)
                            pts_y.append(float(lows[idx]))
                        else:
                            pts_x.append(idx)
                            pts_y.append(float(highs[idx]))

                # Draw dots at each pattern point
                if pts_x and pts_y:
                    ax.scatter(pts_x, pts_y,
                               color=BK_COL, s=60, zorder=8,
                               marker='o', edgecolors='#8B6914',
                               linewidths=1.5, alpha=0.95)

                    # Connect the dots with a thin line
                    ax.plot(pts_x, pts_y,
                            color=BK_COL, lw=1.0,
                            linestyle='--', alpha=0.5, zorder=7)

                    # Label each point (L1, L2 for Double Bottom etc)
                    labels_map = {
                        2: ['L1', 'L2'],     # Double Bottom
                        3: ['LS', 'H', 'RS'],  # Head and Shoulders
                        4: ['L1', 'H1', 'L2', 'H2'],
                        6: ['L1', 'H1', 'L2', 'H2', 'L3', 'H3'],
                    }
                    pt_labels = labels_map.get(len(pts_x),
                                [f'P{i+1}' for i in range(len(pts_x))])

                    for px, py, lbl in zip(pts_x, pts_y, pt_labels):
                        offset = -8 if 'BULL' in pat.get('direction','') else 8
                        ax.annotate(lbl,
                            xy=(px, py),
                            xytext=(px, py),
                            fontsize=6.5, color='#8B6914',
                            fontweight='bold', ha='center',
                            va='top' if 'BULL' in pat.get('direction','') else 'bottom',
                            fontfamily='monospace',
                            bbox=dict(facecolor='#fffde7', edgecolor='#f1c40f',
                                      alpha=0.85, pad=1,
                                      boxstyle='round,pad=0.2'),
                            zorder=9)

                    # Draw neckline as a line connecting the actual neckline level
                    if pat.get('neckline') and len(pts_x) >= 2:
                        nl_val = pat['neckline']
                        # Draw neckline spanning the pattern
                        nl_x0 = max(0, min(pts_x) - 2)
                        nl_x1 = min(n-1, max(pts_x) + proj_extend)
                        proj_extend = min(15, n - max(pts_x) - 1)
                        ax.plot([nl_x0, nl_x1], [nl_val, nl_val],
                                color='#e67e22', lw=2.0,
                                linestyle='-', alpha=0.8, zorder=6,
                                label='_nolegend_')
        except Exception:
            pass

    # ── BROOKS PA SIGNALS — Teal dashed lines ─────────────────────────────
    BR_COL = '#1abc9c'
    for si, sig in enumerate(brooks_sigs[:3]):
        try:
            nums = _re.findall(r'\d+\.?\d*', str(sig.get('entry', '')))
            if nums:
                ev = float(nums[0])
                lbl = f"[PA] {sig['name'][8:][:14]}: {ev:.0f}"
                ln, = ax.plot([0, n-1], [ev, ev],
                              color=BR_COL, linestyle='--',
                              linewidth=1.5, alpha=0.85, zorder=5)
                ax.text(n * 0.55 + si * n * 0.05, ev, f" {lbl}",
                        color=BR_COL, fontsize=7, va='top',
                        fontfamily='monospace',
                        bbox=dict(facecolor='#f0fffd', edgecolor=BR_COL,
                                  alpha=0.8, pad=1))
                legend_items.append((ln, lbl))

            # Stop line
            s_nums = _re.findall(r'\d+\.?\d*', str(sig.get('stop', '')))
            if s_nums:
                sv = float(s_nums[0])
                ax.plot([0, n-1], [sv, sv],
                        color='#e74c3c', linestyle=':', linewidth=1.0, alpha=0.5, zorder=4)
        except Exception:
            pass

    # ── QUANT SIGNALS — Blue dotted lines ─────────────────────────────────
    QT_COL = '#3498db'
    # Show pivot points from Kakushadze signal if present
    for sig in quant_sigs:
        if 'Pivot' in sig['name']:
            try:
                nums = _re.findall(r'\d+\.?\d*', sig['value'])
                vals_labeled = _re.findall(
                    r'(Pivot|R1|R2|S1|S2)=(\d+\.?\d*)', sig['value'])
                for label, val_str in vals_labeled:
                    val = float(val_str)
                    col = ('#3498db' if 'Pivot' in label else
                           '#e67e22' if 'R' in label else '#9b59b6')
                    ax.plot([0, n-1], [val, val],
                            color=col, linestyle=':', linewidth=1.0, alpha=0.6, zorder=4)
                    ax.text(n * 0.85, val, f" {label}:{val:.0f}",
                            color=col, fontsize=6, va='bottom',
                            fontfamily='monospace')
            except Exception:
                pass
            break

    # ── COMPLETION BADGE (top-left) ────────────────────────────────────────
    badges = []
    if bulkowski_pats:
        p0   = bulkowski_pats[0]
        comp = p0.get('completion', {})
        st   = comp.get('status', '')
        pct  = comp.get('pct', 0)
        if st:
            badges.append((f"BK: {st} ({pct}%)", comp.get('color', BK_COL)))
    if brooks_sigs:
        badges.append((f"PA: {brooks_sigs[0]['signal']}", BR_COL))

    for bi, (txt, col) in enumerate(badges[:2]):
        ax.text(0.01, 0.97 - bi * 0.06, txt,
                transform=ax.transAxes,
                color=col, fontsize=7.5,
                verticalalignment='top',
                bbox=dict(boxstyle='round,pad=0.3',
                          facecolor='#0d1117',
                          edgecolor=col, alpha=0.9))

    # ── STREET SMARTS SIGNALS — Sienna/Brown lines ───────────────────────────
    SS_COL_CHART = '#8B4513'
    if street_smarts_sigs:
        for si, sig in enumerate(street_smarts_sigs[:4]):
            try:
                # Entry line
                en_nums = _re.findall(r'\d+\.?\d*', str(sig.get('entry', '')))
                if en_nums:
                    ev = float(en_nums[0])
                    lbl = f"[SS] {sig['name'][15:][:14]}: {ev:.0f}"
                    ax.plot([0, n-1], [ev, ev],
                            color=SS_COL_CHART, linestyle=(0, (5, 2)),
                            linewidth=1.6, alpha=0.88, zorder=5)
                    ax.text(n * 0.30 + si * n * 0.06, ev, f" {lbl}",
                            color=SS_COL_CHART, fontsize=7, va='bottom',
                            fontfamily='monospace',
                            bbox=dict(facecolor='#fff8ee',
                                      edgecolor=SS_COL_CHART,
                                      alpha=0.85, pad=1))

                # Stop line
                st_nums = _re.findall(r'\d+\.?\d*', str(sig.get('stop', '')))
                if st_nums:
                    sv = float(st_nums[0])
                    ax.plot([0, n-1], [sv, sv],
                            color='#e74c3c', linestyle=':', linewidth=1.0,
                            alpha=0.55, zorder=4)
                    ax.text(n * 0.01, sv, f" SS Stop: {sv:.0f}",
                            color='#e74c3c', fontsize=6.5, va='bottom',
                            fontfamily='monospace')

                # Target line
                tg_nums = _re.findall(r'\d+\.?\d*', str(sig.get('target', '')))
                if tg_nums:
                    tv = float(tg_nums[0])
                    ax.plot([0, n-1], [tv, tv],
                            color='#27ae60', linestyle='-.',
                            linewidth=1.1, alpha=0.55, zorder=4)
                    ax.text(n * 0.01, tv, f" SS Target: {tv:.0f}",
                            color='#27ae60', fontsize=6.5, va='bottom',
                            fontfamily='monospace')
            except Exception:
                pass

    # ── COLOR LEGEND (bottom-left) ─────────────────────────────────────────
    legend_labels = [
        plt.Line2D([0], [0], color=BK_COL,        lw=2,   ls='-',         label='Bulkowski Pattern'),
        plt.Line2D([0], [0], color=BR_COL,        lw=1.5, ls='--',        label='Brooks PA Signal'),
        plt.Line2D([0], [0], color=SS_COL_CHART,  lw=1.6, ls=(0,(5,2)),   label='Street Smarts Signal'),
        plt.Line2D([0], [0], color='#3498db',     lw=1,   ls=':',         label='Quant Pivots'),
        plt.Line2D([0], [0], color='#e74c3c',     lw=1,   ls=':',         label='Stop Level'),
        plt.Line2D([0], [0], color='#2ecc71',     lw=1,   ls='-.',        label='Target Level'),
    ]
    ax.legend(handles=legend_labels,
              loc='upper right', fontsize=7,
              facecolor='#161b22', labelcolor='white',
              framealpha=0.9, edgecolor='#555', ncol=1)

    # ── Styling ────────────────────────────────────────────────────────────
    q_b = sum(1 for s in quant_sigs if s['color'] == '#2ecc71')
    q_r = sum(1 for s in quant_sigs if s['color'] == '#e74c3c')
    ss_count = len(street_smarts_sigs) if street_smarts_sigs else 0
    ax.set_title(
        f"BK:{len(bulkowski_pats)}  PA:{len(brooks_sigs)}  SS:{ss_count}  "
        f"Quant: ▲{q_b} bullish  ▼{q_r} bearish",
        color='#1a1d23', fontsize=9, pad=6)
    ax.tick_params(colors='#444444', labelsize=7)
    for spine in ax.spines.values():
        spine.set_edgecolor('#cccccc')

    date_labels = (df['Date'].astype(str).values
                   if 'Date' in df.columns else [str(i) for i in dates])
    step = max(1, n // 10)
    ax.set_xticks(list(dates)[::step])
    ax.set_xticklabels([date_labels[i][:10] for i in range(0, n, step)],
                       rotation=30, ha='right', fontsize=7, color='#555')
    ax.set_ylabel('Price', color='#444', fontsize=9)
    try:
        fig.tight_layout(pad=0.5)
    except Exception:
        pass



# ─────────────────────────────────────────────────────────────────────────────
#  QUANT FORECAST ENGINE
#  Source: Kakushadze & Serur — 151 Trading Strategies (2018)
#  Aggregates all 16 quant signals into a unified forecast:
#   1. Signal agreement score (0–100)
#   2. Bull/bear/neutral counts and weighted direction
#   3. Scenario targets (bull continuation vs mean reversion)
#   4. Individual signal time horizons and expected moves
#   5. Z-score band and pivot levels for chart overlay
#   6. Position sizing guidance from Vol-Weighted Trend
# ─────────────────────────────────────────────────────────────────────────────

# Time horizon for each signal type (trading days)
QUANT_HORIZONS = {
    'Internal Bar Strength':       1,    # next-day mean reversion
    'IBS':                         1,
    'Pivot Point':                  1,    # intraday/next day
    'Short-Term Contrarian':        5,    # 5-day mean reversion
    'Z-Score':                      5,    # short-term mean reversion
    'Momentum Pinball':             3,
    'Single MA':                   60,    # trend filter — medium term
    'Dual MA':                     60,
    'Three MA':                    60,
    'Donchian':                    20,
    'Trend Following':             20,
    'Dual Momentum':               30,
    'Risk-Adjusted Momentum':      30,
    'Vol-Weighted':                20,
    'Return Skewness':             30,
    'Price Momentum':              60,
    'Historical Volatility':       20,
}

# Expected move % per signal based on Kakushadze research
QUANT_EXPECTED_MOVES = {
    'Internal Bar Strength':  2.0,
    'IBS':                    2.0,
    'Pivot Point':            1.5,
    'Short-Term Contrarian':  3.0,
    'Z-Score':                4.0,
    'Single MA':             12.0,
    'Dual MA':               15.0,
    'Three MA':              15.0,
    'Donchian':               8.0,
    'Trend Following':        8.0,
    'Dual Momentum':         12.0,
    'Risk-Adjusted':         10.0,
    'Vol-Weighted':           8.0,
    'Return Skewness':        5.0,
    'Price Momentum':        12.0,
    'Historical Volatility':  5.0,
}


def compute_quant_forecast(quant_signals, df):
    """
    Aggregate all quant signals into a unified probabilistic forecast.

    Returns dict with:
    - Agreement score, bull/bear counts
    - Weighted target prices
    - Per-signal contribution table
    - Z-score bands, pivot levels
    - Position sizing
    - Time horizon breakdown
    """
    if not quant_signals:
        return None

    closes  = df['Close'].values
    highs   = df['High'].values
    lows    = df['Low'].values
    n       = len(closes)
    curr    = closes[-1]

    # ── Classify each signal ──────────────────────────────────────────────
    bull_sigs  = [s for s in quant_signals if s['color'] == '#2ecc71']
    bear_sigs  = [s for s in quant_signals if s['color'] == '#e74c3c']
    neut_sigs  = [s for s in quant_signals
                  if s['color'] not in ('#2ecc71', '#e74c3c')]
    total      = len(quant_signals)
    bull_count = len(bull_sigs)
    bear_count = len(bear_sigs)
    neut_count = len(neut_sigs)

    # ── Agreement score ───────────────────────────────────────────────────
    dominant     = max(bull_count, bear_count)
    agreement_pct = round(dominant / total * 100) if total > 0 else 50
    is_bull_bias  = bull_count >= bear_count

    # Weighted by signal strength
    bull_strength = sum(s.get('strength', 50) for s in bull_sigs)
    bear_strength = sum(s.get('strength', 50) for s in bear_sigs)
    total_strength= bull_strength + bear_strength
    bull_weight   = bull_strength / total_strength if total_strength > 0 else 0.5

    # ── Pivot levels (from Pivot Point signal) ────────────────────────────
    pivot   = r1 = r2 = s1 = s2 = None
    for sig in quant_signals:
        if 'Pivot' in sig['name']:
            import re as _re
            pairs = _re.findall(r'(Pivot|R1|R2|S1|S2)=(\d+\.?\d*)',
                                sig['value'])
            for label, val in pairs:
                v = float(val)
                if label == 'Pivot': pivot = v
                elif label == 'R1':  r1    = v
                elif label == 'R2':  r2    = v
                elif label == 'S1':  s1    = v
                elif label == 'S2':  s2    = v
            break

    # ── Z-score band ──────────────────────────────────────────────────────
    zscore_val = None
    ma_level   = None
    std_level  = None
    for sig in quant_signals:
        if 'Z-Score' in sig['name']:
            import re as _re
            nums = _re.findall(r'Z-score\s*=\s*([+-]?\d+\.?\d*)', sig['value'])
            if nums:
                zscore_val = float(nums[0])
            break
    if n >= 20:
        ma_level  = float(np.mean(closes[-20:]))
        std_level = float(np.std(closes[-20:]))

    # ── Momentum continuation target ──────────────────────────────────────
    # Based on average expected move weighted by signal agreement
    weighted_move = 0.0
    horizon_sum   = 0
    horizon_count = 0
    for sig in (bull_sigs if is_bull_bias else bear_sigs):
        name = sig['name']
        move = 3.0  # default
        for key, m in QUANT_EXPECTED_MOVES.items():
            if key.lower() in name.lower():
                move = m
                break
        horizon = 20
        for key, h in QUANT_HORIZONS.items():
            if key.lower() in name.lower():
                horizon = h
                break
        strength = sig.get('strength', 50) / 100
        weighted_move  += move * strength
        horizon_sum    += horizon * strength
        horizon_count  += strength

    if horizon_count > 0:
        avg_move    = weighted_move / horizon_count
        avg_horizon = int(horizon_sum / horizon_count)
    else:
        avg_move    = 8.0
        avg_horizon = 20

    # Scenario targets
    bull_target = curr * (1 + avg_move / 100)
    bear_target = curr * (1 - avg_move / 100)
    primary_tgt = bull_target if is_bull_bias else bear_target
    secondary_tgt = bull_target * 1.5 - curr * 0.5 if is_bull_bias else \
                    bear_target * 0.5 + curr * 0.5

    # Mean reversion target (from Z-score)
    if ma_level:
        mr_target = ma_level  # mean reversion = return to mean
    else:
        mr_target = curr

    # ── Per-signal contribution table ─────────────────────────────────────
    contributions = []
    for sig in quant_signals:
        name    = sig['name']
        is_bull = sig['color'] == '#2ecc71'
        is_bear = sig['color'] == '#e74c3c'
        direction = '▲ BULL' if is_bull else ('▼ BEAR' if is_bear else '◆ NEUT')

        # Find horizon
        horizon = 20
        for key, h in QUANT_HORIZONS.items():
            if key.lower() in name.lower():
                horizon = h
                break

        # Find expected move
        exp_move = 3.0
        for key, m in QUANT_EXPECTED_MOVES.items():
            if key.lower() in name.lower():
                exp_move = m
                break

        strength = sig.get('strength', 50)
        stars    = '★' * min(5, max(1, int(strength / 20))) + \
                   '☆' * max(0, 5 - min(5, int(strength / 20)))

        contributions.append({
            'name':      name[:28],
            'direction': direction,
            'strength':  strength,
            'stars':     stars,
            'horizon':   horizon,
            'exp_move':  exp_move,
            'signal':    sig.get('signal', '')[:20],
            'color':     sig['color'],
        })

    # Sort: bull first, then bear, then neutral
    contributions.sort(key=lambda x: (
        0 if '▲' in x['direction'] else
        1 if '▼' in x['direction'] else 2,
        -x['strength']
    ))

    # ── Position sizing from Vol-Weighted signal ──────────────────────────
    vw_score   = None
    size_advice = "STANDARD"
    for sig in quant_signals:
        if 'Vol-Weighted' in sig['name']:
            import re as _re
            nums = _re.findall(r'Score\s*=\s*([+-]?\d+\.?\d*)', sig['value'])
            if nums:
                vw_score = float(nums[0])
                if vw_score >= 0.5:   size_advice = "FULL SIZE"
                elif vw_score >= 0.1: size_advice = "STANDARD"
                elif vw_score <= -0.5:size_advice = "FULL SHORT"
                elif vw_score <= -0.1:size_advice = "REDUCE LONGS"
                else:                 size_advice = "REDUCE — FLAT TREND"
            break

    # ── Overall verdict ───────────────────────────────────────────────────
    if agreement_pct >= 75 and dominant >= 8:
        verdict     = '✅ STRONG CONSENSUS — HIGH CONVICTION TRADE'
        verdict_tag = 'good'
        verdict_det = f"{dominant}/{total} signals agree. Full position size appropriate."
    elif agreement_pct >= 60:
        verdict     = '⚠ MODERATE CONSENSUS — STANDARD SIZE'
        verdict_tag = 'warn'
        verdict_det = f"{dominant}/{total} signals agree. Use standard position size."
    elif agreement_pct >= 50:
        verdict     = '⚠ WEAK CONSENSUS — REDUCE SIZE'
        verdict_tag = 'warn'
        verdict_det = f"Only {dominant}/{total} agree. Mixed signals — reduce size 50%."
    else:
        verdict     = '❌ CONFLICTED SIGNALS — WAIT OR SKIP'
        verdict_tag = 'bad'
        verdict_det = f"Bull={bull_count} Bear={bear_count} — market at decision point. Wait."

    return {
        'curr':            curr,
        'total':           total,
        'bull_count':      bull_count,
        'bear_count':      bear_count,
        'neut_count':      neut_count,
        'agreement_pct':   agreement_pct,
        'is_bull_bias':    is_bull_bias,
        'bull_weight':     bull_weight,
        'primary_tgt':     primary_tgt,
        'secondary_tgt':   secondary_tgt,
        'mr_target':       mr_target,
        'avg_move':        avg_move,
        'avg_horizon':     avg_horizon,
        'pivot':           pivot,
        'r1': r1, 'r2': r2, 's1': s1, 's2': s2,
        'zscore_val':      zscore_val,
        'ma_level':        ma_level,
        'std_level':       std_level,
        'contributions':   contributions,
        'vw_score':        vw_score,
        'size_advice':     size_advice,
        'verdict':         verdict,
        'verdict_tag':     verdict_tag,
        'verdict_detail':  verdict_det,
    }


def draw_quant_forecast_chart(fig, df, qfc):
    """Draw quant forecast chart with projection bands and pivot levels."""
    fig.clear()
    ax = fig.add_subplot(111)
    ax.set_facecolor('#ffffff')
    fig.patch.set_facecolor('#f8f9fa')

    n         = len(df)
    closes    = df['Close'].values
    highs     = df['High'].values
    lows      = df['Low'].values
    opens     = df['Open'].values
    curr      = closes[-1]
    show_bars = min(60, n)
    start_idx = n - show_bars
    dates     = list(range(show_bars))
    o = opens[start_idx:]; h = highs[start_idx:]
    l = lows[start_idx:];  c = closes[start_idx:]

    # ── Draw actual candles ───────────────────────────────────────────────
    for i in range(show_bars):
        color = '#2ecc71' if c[i] >= o[i] else '#e74c3c'
        ax.plot([i, i], [l[i], h[i]], color=color, lw=0.8, zorder=2)
        body_lo = min(o[i], c[i])
        body_hi = max(o[i], c[i])
        if body_hi - body_lo < curr * 0.0001:
            body_hi = body_lo + curr * 0.0001
        rect = plt.Rectangle((i-0.4, body_lo), 0.8, body_hi-body_lo,
                              facecolor=color, edgecolor=color, zorder=3)
        ax.add_patch(rect)

    last_bar  = show_bars - 1
    proj_bars = max(qfc['avg_horizon'], 10)
    proj_end  = last_bar + proj_bars
    is_bull   = qfc['is_bull_bias']

    # ── Forecast zone shading ─────────────────────────────────────────────
    ax.axvspan(last_bar, proj_end,
               alpha=0.05, color='#3498db', zorder=0)
    ax.axvline(x=last_bar, color='#aaaaaa',
               linestyle='--', lw=1.0, alpha=0.5)
    ax.text(last_bar + 0.3, curr * 1.002,
            ' QUANT FORECAST →',
            color='#3498db', fontsize=7,
            fontfamily='monospace', alpha=0.7)

    legend_handles = []

    # ── Z-score mean reversion band ───────────────────────────────────────
    if qfc['ma_level'] and qfc['std_level']:
        ma  = qfc['ma_level']
        std = qfc['std_level']
        # Draw MA line across both actual and forecast
        ax.axhline(y=ma, color='#3498db', lw=1.2,
                   linestyle='--', alpha=0.55, zorder=4)
        ax.text(-0.8, ma, f' MA20\n {ma:,.0f}',
                color='#3498db', fontsize=6.5, va='center',
                fontfamily='monospace')
        # ±2σ bands
        upper2 = ma + 2 * std
        lower2 = ma - 2 * std
        ax.fill_between(range(-1, proj_end+2),
                        lower2, upper2,
                        alpha=0.04, color='#3498db', zorder=0)
        ax.axhline(y=upper2, color='#3498db', lw=0.8,
                   linestyle=':', alpha=0.4)
        ax.axhline(y=lower2, color='#3498db', lw=0.8,
                   linestyle=':', alpha=0.4)
        ax.text(proj_end+0.2, upper2, f' +2σ\n {upper2:,.0f}',
                color='#3498db', fontsize=6, va='center',
                fontfamily='monospace')
        ax.text(proj_end+0.2, lower2, f' -2σ\n {lower2:,.0f}',
                color='#3498db', fontsize=6, va='center',
                fontfamily='monospace')
        legend_handles.append(
            plt.Line2D([0],[0], color='#3498db', lw=1.2,
                       linestyle='--', label='20-day MA'))

    # ── Pivot levels (horizontal across whole chart) ──────────────────────
    pivot_cfg = [
        (qfc.get('r2'), 'R2', '#e67e22', ':'),
        (qfc.get('r1'), 'R1', '#e67e22', '--'),
        (qfc.get('pivot'), 'P',  '#3498db', '-'),
        (qfc.get('s1'), 'S1', '#9b59b6', '--'),
        (qfc.get('s2'), 'S2', '#9b59b6', ':'),
    ]
    for level, label, color, ls in pivot_cfg:
        if level:
            ax.axhline(y=level, color=color, lw=1.0,
                       linestyle=ls, alpha=0.55, zorder=4)
            ax.text(proj_end+0.2, level,
                    f' {label}: {level:,.0f}',
                    color=color, fontsize=6.5, va='center',
                    fontfamily='monospace')

    # ── Primary target ────────────────────────────────────────────────────
    tgt1 = qfc['primary_tgt']
    tgt2 = qfc['secondary_tgt']
    tgt_col = '#27ae60' if is_bull else '#e74c3c'
    ax.plot([last_bar, proj_end], [tgt1, tgt1],
            color=tgt_col, lw=2.0, linestyle='--',
            alpha=0.9, zorder=6)
    move_pct = (tgt1 - curr) / curr * 100
    ax.text(proj_end+0.2, tgt1,
            f' Target 1\n {tgt1:,.0f} ({move_pct:+.1f}%)',
            color=tgt_col, fontsize=7, va='center',
            fontfamily='monospace',
            bbox=dict(facecolor='#f0fff4' if is_bull else '#fff0f0',
                      edgecolor=tgt_col, alpha=0.85, pad=1))
    legend_handles.append(
        plt.Line2D([0],[0], color=tgt_col, lw=2,
                   linestyle='--',
                   label=f"Target ({move_pct:+.1f}%)"))

    # ── Secondary target ─────────────────────────────────────────────────
    ax.plot([last_bar, proj_end], [tgt2, tgt2],
            color=tgt_col, lw=1.2, linestyle='-.',
            alpha=0.6, zorder=5)
    move2_pct = (tgt2 - curr) / curr * 100
    ax.text(proj_end+0.2, tgt2,
            f' T2: {tgt2:,.0f} ({move2_pct:+.1f}%)',
            color=tgt_col, fontsize=6.5, va='center',
            fontfamily='monospace')

    # ── Mean reversion target (if relevant) ──────────────────────────────
    mr = qfc['mr_target']
    if mr and abs(mr - curr) / curr > 0.005:
        ax.plot([last_bar, last_bar + proj_bars//2],
                [curr, mr],
                color='#8e44ad', lw=1.4, linestyle=':',
                alpha=0.6, zorder=4)
        ax.text(last_bar + proj_bars//2 + 0.2, mr,
                f' MR: {mr:,.0f}',
                color='#8e44ad', fontsize=6.5, va='center',
                fontfamily='monospace')

    # ── Directional arrow ─────────────────────────────────────────────────
    arrow_x  = last_bar + proj_bars * 0.55
    arrow_dy = (tgt1 - curr) * 0.7
    ax.annotate('',
        xy=(arrow_x, curr + arrow_dy),
        xytext=(arrow_x, curr),
        arrowprops=dict(
            arrowstyle='->', color='#3498db',
            lw=2.5, mutation_scale=20),
        zorder=7)

    # ── Cone of uncertainty (widens over time) ─────────────────────────────
    vol_daily = float(np.std(np.diff(closes[-20:]) / closes[-21:-1])) if n > 21 else 0.01
    for day in range(1, proj_bars + 1):
        spread = curr * vol_daily * (day ** 0.5)
        alpha  = max(0.01, 0.08 - day * 0.002)
        ax.fill_between(
            [last_bar + day - 1, last_bar + day],
            [curr - spread * (day-1)**0.5, curr - spread * day**0.5],
            [curr + spread * (day-1)**0.5, curr + spread * day**0.5],
            alpha=alpha, color='#95a5a6', zorder=0)

    # ── Agreement badge ───────────────────────────────────────────────────
    agr   = qfc['agreement_pct']
    agr_c = '#2ecc71' if agr >= 70 else ('#f1c40f' if agr >= 50 else '#e74c3c')
    ax.text(0.01, 0.97,
            f"Agreement: {agr}%  ({'▲'*qfc['bull_count']}{'▼'*qfc['bear_count']})",
            transform=ax.transAxes,
            color='white', fontsize=8, fontweight='bold', va='top',
            bbox=dict(facecolor=agr_c, edgecolor=agr_c,
                      alpha=0.92, pad=4, boxstyle='round,pad=0.4'))

    # Direction badge
    dir_txt = f"▲ {qfc['bull_count']} BULL" if is_bull else f"▼ {qfc['bear_count']} BEAR"
    dir_col = '#27ae60' if is_bull else '#e74c3c'
    ax.text(0.01, 0.85, dir_txt,
            transform=ax.transAxes,
            color='white', fontsize=8, fontweight='bold', va='top',
            bbox=dict(facecolor=dir_col, edgecolor=dir_col,
                      alpha=0.90, pad=3, boxstyle='round,pad=0.3'))

    # Time horizon label
    ax.text(last_bar + proj_bars * 0.3, lows[start_idx:].min() * 0.9995,
            f'~{qfc["avg_horizon"]} days',
            color='#3498db', fontsize=7,
            fontfamily='monospace', va='bottom', alpha=0.75)

    # ── X-axis ────────────────────────────────────────────────────────────
    step = max(1, show_bars // 8)
    date_labels = (df['Date'].astype(str).values[start_idx:]
                   if 'Date' in df.columns else
                   [str(i) for i in range(start_idx, n)])
    xticks = list(range(0, show_bars, step))
    ax.set_xticks(xticks)
    ax.set_xticklabels(
        [date_labels[i][:10] for i in xticks],
        rotation=30, ha='right', fontsize=6.5, color='#555')
    ax.set_xlim(-2, proj_end + 9)

    # ── Title & styling ───────────────────────────────────────────────────
    ax.set_title(
        f"Quant Forecast  |  "
        f"{qfc['bull_count']}▲ Bull  {qfc['bear_count']}▼ Bear  "
        f"{qfc['neut_count']}◆ Neutral  |  "
        f"Agreement: {qfc['agreement_pct']}%  |  "
        f"Target: {tgt1:,.0f} ({move_pct:+.1f}%)",
        color='#1a1d23', fontsize=9, pad=6, fontweight='bold')
    ax.tick_params(colors='#555', labelsize=7)
    for spine in ax.spines.values():
        spine.set_edgecolor('#cccccc')
    ax.set_ylabel('Price', color='#555', fontsize=8)
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f'{x:,.0f}'))

    if legend_handles:
        ax.legend(handles=legend_handles,
                  loc='upper left', bbox_to_anchor=(0.01, 0.78),
                  fontsize=7, facecolor='#ffffff',
                  labelcolor='#1a1d23', framealpha=0.9,
                  edgecolor='#cccccc', ncol=1)
    try:
        fig.tight_layout(pad=0.5)
    except Exception:
        pass


def draw_forecast_chart(fig, df, fc, mode='bulkowski'):
    """
    Draw actual OHLC candles + forecast projection on a figure.

    mode = 'bulkowski' : uses pattern completion forecast data
    mode = 'brooks'    : uses Brooks PA signal forecast data

    Projection zone shows:
      - Last N actual candles (context)
      - Forward projection lines for entry, T1, T2, stop
      - Directional arrow
      - Throwback/pullback zone
      - Time window shading
      - Probability label
    """
    fig.clear()
    ax = fig.add_subplot(111)
    ax.set_facecolor('#ffffff')
    fig.patch.set_facecolor('#f8f9fa')

    n       = len(df)
    closes  = df['Close'].values
    highs   = df['High'].values
    lows    = df['Low'].values
    opens   = df['Open'].values
    curr    = closes[-1]

    # ── Show last 60 bars for context ─────────────────────────────────────
    show_bars = min(60, n)
    start_idx = n - show_bars
    dates     = list(range(show_bars))
    o = opens[start_idx:];  h = highs[start_idx:]
    l = lows[start_idx:];   c = closes[start_idx:]

    # ── Draw actual candles ────────────────────────────────────────────────
    for i in range(show_bars):
        color = '#2ecc71' if c[i] >= o[i] else '#e74c3c'
        ax.plot([i, i], [l[i], h[i]], color=color, lw=0.8, zorder=2)
        body_lo = min(o[i], c[i])
        body_hi = max(o[i], c[i])
        if body_hi - body_lo < curr * 0.0001:
            body_hi = body_lo + curr * 0.0001
        rect = plt.Rectangle((i - 0.4, body_lo), 0.8,
                              body_hi - body_lo,
                              facecolor=color, edgecolor=color, zorder=3)
        ax.add_patch(rect)

    # ── Projection parameters ──────────────────────────────────────────────
    last_bar   = show_bars - 1   # last actual bar x-position
    is_bull    = fc.get('is_bull', True)

    # Common forecast levels
    if mode == 'bulkowski':
        entry    = fc.get('neckline') or curr
        stop     = fc.get('target_1') and (
            (fc.get('neckline', curr) - (fc.get('pattern_height', curr*0.05)))
            if is_bull else
            (fc.get('neckline', curr) + (fc.get('pattern_height', curr*0.05))))
        t1       = fc.get('target_1')
        t2       = fc.get('target_2')
        t3       = fc.get('target_3')
        prob     = fc.get('completion_prob', 65)
        tb_prob  = fc.get('throwback_prob', 50)
        tb_level = fc.get('throwback_target')
        n_days   = fc.get('est_completion_days', 20)
        title_extra = f"Completion: {prob}%  |  {fc.get('performance_rank','')}"
        # Stop from pattern
        if fc.get('neckline') and fc.get('pattern_height'):
            if is_bull:
                stop = fc['neckline'] - fc['pattern_height'] * 0.5
            else:
                stop = fc['neckline'] + fc['pattern_height'] * 0.5

    else:  # brooks
        entry    = fc.get('entry_price') or curr
        stop     = fc.get('stop_price')
        t1       = fc.get('t1')
        t2       = fc.get('t2')
        t3       = None
        prob     = fc.get('quality_score', 65)
        tb_prob  = None
        tb_level = None
        n_days   = fc.get('max_hold_bars', 8)
        title_extra = f"Quality: {prob}/100  |  {fc.get('trade_type','').upper()}"

    # Projection x-range (N bars forward)
    proj_bars = max(n_days, 10)
    proj_start = last_bar
    proj_end   = last_bar + proj_bars

    # ── Shade forecast time window ─────────────────────────────────────────
    ax.axvspan(proj_start, proj_end,
               alpha=0.06, color='#9b59b6', zorder=0)
    ax.axvline(x=proj_start, color='#aaaaaa',
               linestyle='--', lw=1.0, alpha=0.6, zorder=1)
    ax.text(proj_start + 0.3,
            ax.get_ylim()[1] if ax.get_ylim()[1] != 0 else curr * 1.01,
            ' FORECAST →',
            color='#9b59b6', fontsize=7, va='top',
            fontfamily='monospace', alpha=0.7)

    legend_handles = []

    # ── Entry / Neckline line ──────────────────────────────────────────────
    if entry:
        lne, = ax.plot([proj_start, proj_end], [entry, entry],
                       color='#f1c40f', lw=2.2, linestyle='-',
                       alpha=0.95, zorder=6)
        ax.text(proj_end + 0.2, entry,
                f' Entry\n {entry:,.2f}',
                color='#f1c40f', fontsize=7, va='center',
                fontfamily='monospace',
                bbox=dict(facecolor='#fffff0', edgecolor='#f1c40f',
                          alpha=0.85, pad=1))
        legend_handles.append(
            plt.Line2D([0],[0], color='#f1c40f', lw=2, label='Entry / Neckline'))

    # ── Stop loss line ─────────────────────────────────────────────────────
    if stop:
        ax.plot([proj_start, proj_end], [stop, stop],
                color='#e74c3c', lw=1.5, linestyle=':',
                alpha=0.85, zorder=5)
        ax.text(proj_end + 0.2, stop,
                f' Stop\n {stop:,.2f}',
                color='#e74c3c', fontsize=7, va='center',
                fontfamily='monospace',
                bbox=dict(facecolor='#fff0f0', edgecolor='#e74c3c',
                          alpha=0.85, pad=1))
        legend_handles.append(
            plt.Line2D([0],[0], color='#e74c3c', lw=1.5,
                       linestyle=':', label='Stop Loss'))

    # ── Target 1 ──────────────────────────────────────────────────────────
    if t1:
        ax.plot([proj_start, proj_end], [t1, t1],
                color='#2ecc71', lw=1.8, linestyle='--',
                alpha=0.9, zorder=5)
        ax.text(proj_end + 0.2, t1,
                f' T1\n {t1:,.2f}',
                color='#2ecc71', fontsize=7, va='center',
                fontfamily='monospace',
                bbox=dict(facecolor='#f0fff4', edgecolor='#2ecc71',
                          alpha=0.85, pad=1))
        legend_handles.append(
            plt.Line2D([0],[0], color='#2ecc71', lw=1.8,
                       linestyle='--', label=f'Target 1 ({t1:,.0f})'))

    # ── Target 2 ──────────────────────────────────────────────────────────
    if t2:
        ax.plot([proj_start, proj_end], [t2, t2],
                color='#27ae60', lw=1.4, linestyle='-.',
                alpha=0.75, zorder=4)
        ax.text(proj_end + 0.2, t2,
                f' T2\n {t2:,.2f}',
                color='#27ae60', fontsize=7, va='center',
                fontfamily='monospace')
        legend_handles.append(
            plt.Line2D([0],[0], color='#27ae60', lw=1.4,
                       linestyle='-.', label=f'Target 2 ({t2:,.0f})'))

    # ── Target 3 (Bulkowski only) ─────────────────────────────────────────
    if t3:
        ax.plot([proj_start, proj_end], [t3, t3],
                color='#1a7a4a', lw=1.0, linestyle=':',
                alpha=0.6, zorder=4)
        ax.text(proj_end + 0.2, t3,
                f' T3\n {t3:,.2f}',
                color='#1a7a4a', fontsize=6.5, va='center',
                fontfamily='monospace')

    # ── Throwback zone (Bulkowski only) ──────────────────────────────────
    if tb_level and tb_prob and mode == 'bulkowski' and entry:
        ax.axhspan(
            min(tb_level, entry) * 0.999,
            max(tb_level, entry) * 1.001,
            xmin=(proj_start) / (proj_end + 5),
            xmax=(proj_start + proj_bars * 0.4) / (proj_end + 5),
            alpha=0.12, color='#e67e22', zorder=1)
        ax.text(proj_start + proj_bars * 0.1, tb_level,
                f' Throwback zone\n ({tb_prob}% prob)',
                color='#e67e22', fontsize=6.5, va='bottom',
                fontfamily='monospace', alpha=0.85)

    # ── Directional arrow ─────────────────────────────────────────────────
    if entry and (t1 or t2):
        target_for_arrow = t1 or t2
        arrow_x    = proj_start + proj_bars * 0.6
        arrow_dy   = target_for_arrow - entry
        ax.annotate('',
            xy=(arrow_x, entry + arrow_dy * 0.85),
            xytext=(arrow_x, entry),
            arrowprops=dict(
                arrowstyle='->', color='#9b59b6',
                lw=2.5, mutation_scale=20),
            zorder=7)

    # ── Probability label box ─────────────────────────────────────────────
    prob_txt = (f"{'Completion' if mode=='bulkowski' else 'Quality'}: {prob}%"
                if mode == 'bulkowski' else f"Quality: {prob}/100")
    prob_col = ('#2ecc71' if prob >= 70 else
                '#f1c40f' if prob >= 50 else '#e74c3c')
    ax.text(0.01, 0.97, prob_txt,
            transform=ax.transAxes,
            color='white', fontsize=9, fontweight='bold',
            va='top',
            bbox=dict(facecolor=prob_col, edgecolor=prob_col,
                      alpha=0.92, pad=4, boxstyle='round,pad=0.4'))

    # ── Direction badge ───────────────────────────────────────────────────
    dir_txt = '▲ BULLISH' if is_bull else '▼ BEARISH'
    dir_col = '#27ae60' if is_bull else '#e74c3c'
    ax.text(0.01, 0.86, dir_txt,
            transform=ax.transAxes,
            color='white', fontsize=8, fontweight='bold',
            va='top',
            bbox=dict(facecolor=dir_col, edgecolor=dir_col,
                      alpha=0.90, pad=3, boxstyle='round,pad=0.3'))

    # ── Time window label ─────────────────────────────────────────────────
    ax.text(proj_start + proj_bars * 0.3,
            ax.get_ylim()[0] if ax.get_ylim()[0] != 0 else curr * 0.99,
            f'~{n_days} {"bars" if mode=="brooks" else "days"}',
            color='#9b59b6', fontsize=7,
            fontfamily='monospace', va='bottom', alpha=0.75)

    # ── X-axis labels ─────────────────────────────────────────────────────
    step = max(1, show_bars // 8)
    date_labels = (df['Date'].astype(str).values[start_idx:]
                   if 'Date' in df.columns else
                   [str(i) for i in range(start_idx, n)])
    xtick_pos   = list(range(0, show_bars, step))
    ax.set_xticks(xtick_pos)
    ax.set_xticklabels(
        [date_labels[i][:10] for i in xtick_pos],
        rotation=30, ha='right', fontsize=6.5, color='#555')

    # Extend x-axis to show projection labels
    ax.set_xlim(-1, proj_end + 8)

    # ── Styling ───────────────────────────────────────────────────────────
    pat_name = fc.get('pattern_name') or fc.get('name', '')
    ax.set_title(
        f"{pat_name}  |  {title_extra}",
        color='#1a1d23', fontsize=9, pad=6, fontweight='bold')
    ax.tick_params(colors='#555555', labelsize=7)
    for spine in ax.spines.values():
        spine.set_edgecolor('#cccccc')
    ax.set_ylabel('Price', color='#555', fontsize=8)
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f'{x:,.0f}'))

    if legend_handles:
        ax.legend(handles=legend_handles,
                  loc='upper left',
                  bbox_to_anchor=(0.01, 0.82),
                  fontsize=7,
                  facecolor='#ffffff',
                  labelcolor='#1a1d23',
                  framealpha=0.9,
                  edgecolor='#cccccc',
                  ncol=1)

    try:
        fig.tight_layout(pad=0.5)
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN GUI APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

class BulkowskiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bulkowski Chart Pattern Analyzer — Encyclopedia of Chart Patterns")
        self.root.configure(bg='#f0f0f0')
        self.root.geometry('1440x960')
        self.df          = None
        self.df_intra    = None
        self.detected    = []
        self.quant_signals  = []
        self.brooks_signals = []
        self.street_smarts  = []
        # Angel One session state
        self._angel_obj     = None
        self._angel_token   = None
        self._angel_feed    = None
        self._angel_config  = {
            'api_key':   'gbjChoIy',
            'client_id': '',
            'password':  '',
            'totp_key':  '',
        }
        # Drawing tool state (set properly in _build_ui)
        self._draw_lines = []
        self._draw_start = None
        self._draw_temp  = None
        self._draw_cid_press   = None
        self._draw_cid_release = None
        self._draw_cid_drag    = None
        self._active_tab = 'daily'
        self._build_ui()

    def _build_ui(self):
        # ── TOP BAR ──
        # ── TOP BAR — Two rows: title row + button row ──
        topbar = tk.Frame(self.root, bg='#1a1d23')
        topbar.pack(fill='x')

        # Row 1: Title
        title_row = tk.Frame(topbar, bg='#1a1d23', pady=4, padx=12)
        title_row.pack(fill='x')
        tk.Label(title_row, text="📊 BULKOWSKI CHART PATTERN ANALYZER",
                 bg='#1a1d23', fg='#f1c40f',
                 font=('Consolas', 12, 'bold')).pack(side='left')
        tk.Label(title_row,
                 text="Encyclopedia of Chart Patterns — Thomas N. Bulkowski (2005)",
                 bg='#1a1d23', fg='#777',
                 font=('Consolas', 9)).pack(side='left', padx=16)

        # Row 2: All buttons — full width, smaller font
        btn_row = tk.Frame(topbar, bg='#1a1d23', pady=3, padx=8)
        btn_row.pack(fill='x')
        btn_frame = btn_row   # alias so rest of code works unchanged

        def _mkbtn(text, cmd, color):
            return tk.Button(btn_frame, text=text, command=cmd,
                             bg=color, fg='white', relief='flat',
                             font=('Consolas', 8, 'bold'),
                             padx=7, pady=4, cursor='hand2',
                             activebackground=color, activeforeground='white')

        _mkbtn("📂 1D Chart",     self._load_csv,           '#2980b9').pack(side='left', padx=2)
        _mkbtn("📂 Intraday",     self._load_intraday,      '#1a7a6e').pack(side='left', padx=2)
        _mkbtn("🔍 Detect",       self._detect,             '#27ae60').pack(side='left', padx=2)
        _mkbtn("📈 Quant",        self._show_quant_signals, '#d35400').pack(side='left', padx=2)
        _mkbtn("📚 Library",      self._show_library,       '#8e44ad').pack(side='left', padx=2)
        _mkbtn("⚖️ R:R",          self._show_rr_calculator, '#c0392b').pack(side='left', padx=2)
        _mkbtn("📐 Brooks PA",    self._show_brooks,           '#2c7a4b').pack(side='left', padx=2)
        _mkbtn("📐 PA Forecast",  self._show_brooks_forecast,   '#1a5c35').pack(side='left', padx=2)
        _mkbtn("📊 Quant Fcast",   self._show_quant_forecast,    '#2471a3').pack(side='left', padx=2)
        _mkbtn("🎯 StreetSmarts", self._show_street_smarts,     '#8B4513').pack(side='left', padx=2)
        _mkbtn("📉 Backtest",     self._show_backtest,           '#922b21').pack(side='left', padx=2)
        _mkbtn("🔌 Angel One",    self._show_angel_one,         '#e67e22').pack(side='left', padx=2)
        _mkbtn("🔮 Forecast",     self._show_forecast,          '#6c3483').pack(side='left', padx=2)
        _mkbtn("❓ Help",          self._show_help,              '#7f8c8d').pack(side='left', padx=2)

        # ── STATUS ──
        self.status_var = tk.StringVar(value="▶ Load a CSV file to begin analysis")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                              bg='#1a1d23', fg='#aaa', font=('Consolas', 9),
                              anchor='w', padx=16, pady=3)
        status_bar.pack(fill='x')

        # ── MAIN PANE ──
        main_pane = tk.PanedWindow(self.root, orient='horizontal',
                                   bg='#e8e8e8', sashrelief='flat',
                                   sashwidth=6)
        main_pane.pack(fill='both', expand=True, padx=8, pady=4)

        # ── LEFT: DUAL CHART NOTEBOOK ──
        chart_outer = tk.Frame(main_pane, bg='#f5f5f5', relief='flat', bd=1)
        main_pane.add(chart_outer, width=780)

        # Tab strip (manual tabs — lighter than ttk.Notebook for dark theme)
        tab_bar = tk.Frame(chart_outer, bg='#e8e8e8', pady=0)
        tab_bar.pack(fill='x')

        self._tab_daily_btn = tk.Button(
            tab_bar, text="📅 1D Chart",
            bg='#f1c40f', fg='#0d1117',
            font=('Consolas', 9, 'bold'), relief='flat',
            padx=14, pady=5, cursor='hand2',
            command=lambda: self._switch_tab('daily'))
        self._tab_daily_btn.pack(side='left')

        self._tab_intra_btn = tk.Button(
            tab_bar, text="⏱ Intraday (5-min)",
            bg='#d0e8f0', fg='#777',
            font=('Consolas', 9, 'bold'), relief='flat',
            padx=14, pady=5, cursor='hand2',
            command=lambda: self._switch_tab('intraday'))
        self._tab_intra_btn.pack(side='left', padx=2)

        # Intraday status label
        self._intra_status = tk.Label(
            tab_bar, text="  (no intraday data — click '📂 Intraday Chart' to load)",
            bg='#e8e8e8', fg='#777',
            font=('Consolas', 8))
        self._intra_status.pack(side='left', padx=8)

        # Daily chart frame
        chart_frame = tk.Frame(chart_outer, bg='#e8e8e8')
        chart_frame.pack(fill='both', expand=True)

        # ── CHART TOOLBAR ROW ────────────────────────────────────────────────
        toolbar_frame = tk.Frame(chart_frame, bg='#f0f0f0', pady=2)
        toolbar_frame.pack(fill='x')

        self.fig = Figure(figsize=(9, 5.5), dpi=88)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)

        # Matplotlib built-in navigation toolbar (zoom/pan/home/save)
        self._nav_toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self._nav_toolbar.config(background='#f0f0f0')
        self._nav_toolbar.update()

        # Custom drawing tools toolbar
        draw_bar = tk.Frame(toolbar_frame, bg='#f0f0f0')
        draw_bar.pack(side='right', padx=6)

        tk.Label(draw_bar, text="Draw:", bg='#f0f0f0', fg='#555',
                 font=('Consolas', 8)).pack(side='left', padx=2)

        self._draw_mode = tk.StringVar(value='none')
        self._draw_lines = []      # list of drawn line objects
        self._draw_start = None    # start point for line drawing
        self._draw_temp  = None    # temp line while dragging

        draw_tools = [
            ('━ H-Line',  'hline',   '#2980b9'),
            ('╱ Trendline','trendline','#27ae60'),
            ('▭ Rect',    'rect',    '#8e44ad'),
            ('✕ Clear',   'clear',   '#e74c3c'),
        ]

        self._draw_btns = {}
        for label, mode, color in draw_tools:
            if mode == 'clear':
                btn = tk.Button(draw_bar, text=label,
                                command=self._clear_drawings,
                                bg=color, fg='white',
                                font=('Consolas', 7, 'bold'),
                                relief='flat', padx=6, pady=2,
                                cursor='hand2')
            else:
                btn = tk.Button(draw_bar, text=label,
                                command=lambda m=mode: self._set_draw_mode(m),
                                bg='#e0e0e0', fg='#333',
                                font=('Consolas', 7, 'bold'),
                                relief='flat', padx=6, pady=2,
                                cursor='hand2')
            btn.pack(side='left', padx=2)
            self._draw_btns[mode] = btn

        self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=2, pady=2)

        # ── CROSSHAIR STATE ──
        self._crosshair_h    = None
        self._crosshair_v    = None
        self._crosshair_xbox = None
        self._crosshair_ybox = None
        self._crosshair_ohlc = None
        self._cid_move       = None
        self._cid_leave      = None

        # ── CROSSHAIR INFO BAR ──
        self._crosshair_bar = tk.Label(
            chart_frame,
            text="  Move mouse over chart to see OHLC values",
            bg='#e0e0e0', fg='#555555',
            font=('Consolas', 9), anchor='w', padx=8, pady=3
        )
        self._crosshair_bar.pack(fill='x')

        # Intraday chart frame (hidden until tab switched)
        self._intra_frame = tk.Frame(chart_outer, bg='#e8e8e8')

        # ── Intraday toolbar (zoom + scroll) ─────────────────────────────────
        _itb = tk.Frame(self._intra_frame, bg='#1a1d23', pady=3)
        _itb.pack(fill='x')

        def _intra_zoom_in():
            self._intra_window_size = max(30, self._intra_window_size - 30)
            self._clamp_intra_offset()
            self._draw_intraday_chart()

        def _intra_zoom_out():
            n = len(self.df_intra) if self.df_intra is not None else 1000
            self._intra_window_size = min(n, self._intra_window_size + 30)
            self._clamp_intra_offset()
            self._draw_intraday_chart()

        def _intra_scroll_left():
            self._intra_offset = max(0, self._intra_offset - max(1, self._intra_window_size // 4))
            self._draw_intraday_chart()

        def _intra_scroll_right():
            n = len(self.df_intra) if self.df_intra is not None else 1000
            self._intra_offset = min(n - self._intra_window_size, self._intra_offset + max(1, self._intra_window_size // 4))
            self._draw_intraday_chart()

        def _intra_go_latest():
            n = len(self.df_intra) if self.df_intra is not None else 1000
            self._intra_offset = max(0, n - self._intra_window_size)
            self._draw_intraday_chart()

        def _intra_go_start():
            self._intra_offset = 0
            self._draw_intraday_chart()

        def _mk_itbtn(parent, txt, cmd, bg='#2c3e50', fg='white'):
            b = tk.Button(parent, text=txt, command=cmd,
                          bg=bg, fg=fg, font=('Consolas', 9, 'bold'),
                          relief='flat', padx=8, pady=2, cursor='hand2')
            b.pack(side='left', padx=2)
            return b

        _mk_itbtn(_itb, '|◀ Start',  _intra_go_start,  '#2c3e50')
        _mk_itbtn(_itb, '◀ ¼ Back',  _intra_scroll_left, '#2c3e50')
        _mk_itbtn(_itb, '🔍+',        _intra_zoom_in,   '#1a5276')
        _mk_itbtn(_itb, '🔍−',        _intra_zoom_out,  '#1a5276')
        _mk_itbtn(_itb, '¼ Fwd ▶',   _intra_scroll_right, '#2c3e50')
        _mk_itbtn(_itb, 'Latest ▶|', _intra_go_latest,  '#145a32')

        self._intra_window_label = tk.Label(_itb, text="",
            bg='#1a1d23', fg='#aaaaaa', font=('Consolas', 8), padx=10)
        self._intra_window_label.pack(side='left')

        # ── Scrollbar ─────────────────────────────────────────────────────────
        self._intra_scrollbar = tk.Scale(
            self._intra_frame, orient='horizontal',
            from_=0, to=100, resolution=1,
            bg='#1a1d23', fg='#aaaaaa', troughcolor='#2c3e50',
            highlightthickness=0, showvalue=0, sliderlength=30,
            command=lambda v: self._on_intra_scroll(int(float(v))))
        self._intra_scrollbar.pack(fill='x', padx=2)

        self.fig_intra  = Figure(figsize=(8, 5), dpi=90)
        self.canvas_intra = FigureCanvasTkAgg(self.fig_intra, master=self._intra_frame)
        self.canvas_intra.get_tk_widget().pack(fill='both', expand=True, padx=2, pady=2)

        self._intra_xhbar = tk.Label(
            self._intra_frame,
            text="  Load intraday CSV to enable this chart",
            bg='#e0e0e0', fg='#777',
            font=('Consolas', 9), anchor='w', padx=8, pady=3)
        self._intra_xhbar.pack(fill='x')

        # Crosshair for intraday
        self._cid_move_intra  = None
        self._cid_leave_intra = None
        self._ch_h_intra = self._ch_v_intra = None
        self._ch_xb_intra = self._ch_yb_intra = None

        # Intraday window state (sliding window for large datasets)
        self._intra_window_size = 120   # bars visible at once
        self._intra_offset      = 0     # leftmost bar index

        # Annotation panel — shows key levels from daily on intraday chart
        self._annotation_panel = tk.Frame(chart_outer, bg='#e8e8e8')
        self._annotation_label = tk.Label(
            self._annotation_panel,
            text="",
            bg='#e8e8e8', fg='#b8600a',
            font=('Consolas', 8), anchor='w', padx=8, pady=2,
            wraplength=800, justify='left')
        self._annotation_label.pack(fill='x')

        # Bind crosshair events for daily chart
        self._setup_crosshair()

        # ── RIGHT: RESULTS PANEL ──
        right_frame = tk.Frame(main_pane, bg='#f5f5f5')
        main_pane.add(right_frame, width=500)

        # ── SIGNAL TYPE SELECTOR ──────────────────────────────────────────
        sel_frame = tk.Frame(right_frame, bg='#f5f5f5', pady=4)
        sel_frame.pack(fill='x', padx=4)

        tk.Label(sel_frame, text="SHOW:",
                 bg='#f5f5f5', fg='#666666',
                 font=('Consolas', 8, 'bold')).pack(side='left', padx=(0, 6))

        self._signal_mode = tk.StringVar(value='all')

        modes = [
            ('All',           'all',         '#f1c40f', '#1a1a0a'),
            ('Bulkowski',     'bulkowski',   '#f1c40f', '#1a1a0a'),
            ('Brooks PA',     'brooks',      '#1abc9c', '#001a18'),
            ('Quant',         'quant',       '#3498db', '#00101a'),
            ('Street Smarts', 'streetsmarts','#cd853f', '#1a0e00'),
        ]
        self._mode_btns = {}
        for label, mode, fg, abg in modes:
            btn = tk.Radiobutton(
                sel_frame,
                text=label,
                value=mode,
                variable=self._signal_mode,
                command=self._refresh_signal_view,
                bg='#f0f0f0',
                fg=fg,
                selectcolor='#dddddd',
                activebackground='#f0f0f0',
                activeforeground=fg,
                font=('Consolas', 8, 'bold'),
                relief='flat',
                cursor='hand2',
                indicatoron=False,
                padx=8, pady=3,
            )
            btn.pack(side='left', padx=2)
            self._mode_btns[mode] = btn

        # Update button appearance based on selection
        def _update_btn_styles(*args):
            mode = self._signal_mode.get()
            style_map = {
                'all':          ('#f1c40f', '#1a1400'),
                'bulkowski':    ('#f1c40f', '#1a1400'),
                'brooks':       ('#1abc9c', '#001a18'),
                'quant':        ('#3498db', '#00101a'),
                'streetsmarts': ('#cd853f', '#1a0e00'),
            }
            for m, btn in self._mode_btns.items():
                fg_c, bg_c = style_map[m]
                if m == mode:
                    btn.config(bg=bg_c, fg=fg_c,
                               relief='solid', bd=1)
                else:
                    btn.config(bg='#f5f5f5', fg='#777',
                               relief='flat', bd=0)
        self._signal_mode.trace('w', _update_btn_styles)
        _update_btn_styles()

        # Pattern list — compact height so detail panel gets more space
        tk.Label(right_frame, text="DETECTED SIGNALS",
                 bg='#f5f5f5', fg='#b8600a',
                 font=('Consolas', 10, 'bold'),
                 pady=4).pack(fill='x')

        list_frame = tk.Frame(right_frame, bg='#f5f5f5')
        list_frame.pack(fill='x', padx=4)

        scrollbar_x = tk.Scrollbar(list_frame, orient='vertical')
        self.pattern_listbox = tk.Listbox(
            list_frame, yscrollcommand=scrollbar_x.set,
            bg='#ffffff', fg='#1a1d23',
            selectbackground='#2980b9',
            font=('Consolas', 9),
            height=6, relief='flat',
            activestyle='none'
        )
        scrollbar_x.config(command=self.pattern_listbox.yview)
        scrollbar_x.pack(side='right', fill='y')
        self.pattern_listbox.pack(fill='x')
        self.pattern_listbox.bind('<<ListboxSelect>>', self._on_pattern_select)

        # Detail panel — takes all remaining vertical space
        tk.Label(right_frame, text="PATTERN DETAILS + TRADING PLAN",
                 bg='#f5f5f5', fg='#b8600a',
                 font=('Consolas', 10, 'bold'),
                 pady=4).pack(fill='x')

        detail_frame = tk.Frame(right_frame, bg='#f5f5f5')
        detail_frame.pack(fill='both', expand=True, padx=4, pady=2)

        self.detail_text = scrolledtext.ScrolledText(
            detail_frame,
            bg='#ffffff', fg='#1a1d23',
            font=('Consolas', 8),
            wrap=tk.WORD,
            relief='flat',
            padx=8, pady=6,
            insertbackground='white'
        )
        self.detail_text.pack(fill='both', expand=True)

        # Color tags
        self.detail_text.tag_config('header',   foreground='#f1c40f', font=('Consolas', 9, 'bold'))
        self.detail_text.tag_config('bullish',  foreground='#2ecc71', font=('Consolas', 8, 'bold'))
        self.detail_text.tag_config('bearish',  foreground='#e74c3c', font=('Consolas', 8, 'bold'))
        self.detail_text.tag_config('neutral',  foreground='#3498db', font=('Consolas', 8, 'bold'))
        self.detail_text.tag_config('label',    foreground='#666666', font=('Consolas', 8))
        self.detail_text.tag_config('value',    foreground='#1a1d23', font=('Consolas', 8))
        self.detail_text.tag_config('entry',    foreground='#2ecc71', font=('Consolas', 8, 'bold'))
        self.detail_text.tag_config('stop',     foreground='#e74c3c', font=('Consolas', 8, 'bold'))
        self.detail_text.tag_config('target',   foreground='#f1c40f', font=('Consolas', 8, 'bold'))
        self.detail_text.tag_config('warning',  foreground='#e67e22', font=('Consolas', 8))
        self.detail_text.tag_config('best',     foreground='#9b59b6', font=('Consolas', 8))
        self.detail_text.tag_config('rule',     foreground='#1a6fa8', font=('Consolas', 7))
        self.detail_text.tag_config('divider',  foreground='#aaaaaa', font=('Consolas', 7))

        # Initial message
        self._show_welcome()

    # ─────────────────────────────────────────────────────────────────────────
    #  DUAL CHART — TAB SWITCHING & INTRADAY LOAD
    # ─────────────────────────────────────────────────────────────────────────

    def _switch_tab(self, tab):
        """Switch between daily and intraday chart views."""
        self._active_tab = tab
        if tab == 'daily':
            self._intra_frame.pack_forget()
            self._annotation_panel.pack_forget()
            # Repack daily
            self.canvas.get_tk_widget().master.pack(fill='both', expand=True)
            self._tab_daily_btn.config(bg='#f1c40f', fg='#0d1117')
            self._tab_intra_btn.config(bg='#d0e8f0', fg='#777')
        else:
            if self.df_intra is None:
                messagebox.showinfo("No Intraday Data",
                    "Click '📂 Intraday Chart' to load a 5-min CSV first.")
                return
            self.canvas.get_tk_widget().master.pack_forget()
            self._annotation_panel.pack(fill='x')
            self._intra_frame.pack(fill='both', expand=True)
            self._tab_daily_btn.config(bg='#cccccc', fg='#555555')
            self._tab_intra_btn.config(bg='#1a7a6e', fg='#ffffff')
            self._draw_intraday_chart()

    def _load_intraday(self):
        """Load a 5-min (or any intraday) CSV. Keeps daily data intact."""
        filepath = filedialog.askopenfilename(
            title="Select Intraday CSV (5-min, 15-min, etc.)",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not filepath:
            return
        try:
            df = pd.read_csv(filepath)
            df.columns = [c.strip().capitalize() for c in df.columns]
            col_map = {}
            for col in df.columns:
                cl = col.lower()
                if 'date' in cl or 'time' in cl: col_map[col] = 'Date'
                elif cl in ('open','o'):          col_map[col] = 'Open'
                elif cl in ('high','h'):          col_map[col] = 'High'
                elif cl in ('low','l'):           col_map[col] = 'Low'
                elif cl in ('close','c'):         col_map[col] = 'Close'
                elif 'vol' in cl:                 col_map[col] = 'Volume'
            df.rename(columns=col_map, inplace=True)
            required = ['Open', 'High', 'Low', 'Close']
            for r in required:
                if r not in df.columns:
                    raise ValueError(f"Missing column: {r}")
            for col in required:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            df.dropna(subset=required, inplace=True)
            if 'Date' not in df.columns:
                df['Date'] = range(len(df))
            try:
                df['Date'] = pd.to_datetime(df['Date'])
                df.sort_values('Date', ascending=True, inplace=True)
                df['Date'] = df['Date'].dt.strftime('%Y-%m-%d %H:%M')
            except Exception:
                pass
            df.reset_index(drop=True, inplace=True)
            self.df_intra = df
            # Auto-scroll to latest bars on load
            self._intra_window_size = min(120, len(df))
            self._intra_offset = max(0, len(df) - self._intra_window_size)
            fname = filepath.split('/')[-1].split('\\')[-1]
            self._intra_status.config(
                text=f"  ✅ {fname} — {len(df)} bars",
                fg='#1abc9c')
            self.status_var.set(
                f"✅ Intraday loaded: {fname} ({len(df)} bars). "
                f"Click '⏱ Intraday' tab to view.")
            # Auto-switch to intraday tab
            self._switch_tab('intraday')
            self._setup_intraday_crosshair()
        except Exception as e:
            messagebox.showerror("Intraday Load Error",
                f"Could not load file:\n{str(e)}\n\n"
                f"Need columns: Date, Open, High, Low, Close")

    def _clamp_intra_offset(self):
        """Keep offset within valid range for current window size."""
        if self.df_intra is None:
            return
        n = len(self.df_intra)
        self._intra_window_size = max(30, min(n, self._intra_window_size))
        self._intra_offset = max(0, min(n - self._intra_window_size, self._intra_offset))

    def _on_intra_scroll(self, val):
        """Scrollbar moved — update offset proportionally."""
        if self.df_intra is None:
            return
        n   = len(self.df_intra)
        win = self._intra_window_size
        max_offset = max(0, n - win)
        self._intra_offset = int(val / 100.0 * max_offset)
        self._draw_intraday_chart()

    def _draw_intraday_chart(self):
        """Draw the intraday chart with daily key levels overlaid (windowed view)."""
        if self.df_intra is None:
            return

        full_df = self.df_intra
        n_total = len(full_df)

        # ── Clamp window ──────────────────────────────────────────────────────
        self._clamp_intra_offset()
        start = self._intra_offset
        end   = min(n_total, start + self._intra_window_size)
        df    = full_df.iloc[start:end].reset_index(drop=True)

        # ── Update scrollbar position (suppress recursive callback) ──────────
        max_offset = max(1, n_total - self._intra_window_size)
        pct = int(self._intra_offset / max_offset * 100) if max_offset > 0 else 100
        self._intra_scrollbar.config(to=100)
        self._intra_scrollbar.set(pct)

        # ── Window info label ─────────────────────────────────────────────────
        self._intra_window_label.config(
            text=f"  Bars {start+1}–{end} of {n_total}  |  Window: {len(df)}")

        self.fig_intra.clear()
        ax = self.fig_intra.add_subplot(111)
        ax.set_facecolor('#0d1117')
        self.fig_intra.patch.set_facecolor('#1a1d23')

        dates  = range(len(df))
        o = df['Open'].values
        h = df['High'].values
        l = df['Low'].values
        c = df['Close'].values

        # Draw candlesticks — body width scales with window size
        body_w = max(0.2, min(0.45, 30 / len(df)))
        for i in dates:
            color = '#2ecc71' if c[i] >= o[i] else '#e74c3c'
            ax.plot([i, i], [l[i], h[i]], color=color, linewidth=0.7, zorder=2)
            body_lo = min(o[i], c[i])
            body_hi = max(o[i], c[i])
            if body_hi - body_lo < 0.01:
                body_hi = body_lo + 0.01
            rect = plt.Rectangle((i - body_w, body_lo), body_w * 2, body_hi - body_lo,
                                  facecolor=color, edgecolor=color, zorder=3)
            ax.add_patch(rect)

        # ── Overlay key levels from daily chart ──────────────────────────────
        overlay_lines = []
        ann_text_parts = []

        if self.detected:
            for pat in self.detected[:3]:
                if 'neckline' in pat:
                    nl = pat['neckline']
                    ax.axhline(y=nl, color='#f1c40f', linestyle='-',
                               alpha=0.85, linewidth=1.5,
                               label=f"Neckline: {nl:.2f}")
                    overlay_lines.append(('NECKLINE / ENTRY', nl, '#f1c40f'))

                if 'pattern_low' in pat:
                    sl = pat['pattern_low'] * 0.99
                    ax.axhline(y=sl, color='#e74c3c', linestyle=':',
                               alpha=0.7, linewidth=1.2,
                               label=f"Stop: {sl:.2f}")
                    overlay_lines.append(('STOP LOSS', sl, '#e74c3c'))

                import re
                try:
                    nums = re.findall(r'\d+\.?\d*', str(pat.get('target', '')))
                    if nums:
                        tgt = float(nums[0])
                        ax.axhline(y=tgt, color='#2ecc71', linestyle='-.',
                                   alpha=0.7, linewidth=1.2,
                                   label=f"Target: {tgt:.2f}")
                        overlay_lines.append(('TARGET', tgt, '#2ecc71'))
                except Exception:
                    pass

        # Pivot points from daily
        if self.df is not None and len(self.df) >= 2:
            prev = self.df.iloc[-1]
            ph, pl, pc_d = prev['High'], prev['Low'], prev['Close']
            pvt  = (ph + pl + pc_d) / 3
            r1   = 2 * pvt - pl
            s1   = 2 * pvt - ph
            ax.axhline(y=pvt, color='#3498db', linestyle='--',
                       alpha=0.5, linewidth=1.0,
                       label=f"Daily Pivot: {pvt:.2f}")
            ax.axhline(y=r1, color='#e67e22', linestyle='--',
                       alpha=0.4, linewidth=0.8,
                       label=f"R1: {r1:.2f}")
            ax.axhline(y=s1, color='#9b59b6', linestyle='--',
                       alpha=0.4, linewidth=0.8,
                       label=f"S1: {s1:.2f}")
            overlay_lines += [
                ('DAILY PIVOT', pvt, '#3498db'),
                ('DAILY R1',    r1,  '#e67e22'),
                ('DAILY S1',    s1,  '#9b59b6'),
            ]

        # Build annotation text
        if overlay_lines:
            parts = [f"{name}: {val:.2f}" for name, val, _ in overlay_lines]
            ann = "  Key Levels →  " + "    |    ".join(parts)
            self._annotation_label.config(text=ann)
            self._annotation_panel.pack(fill='x', before=self._intra_frame)
        else:
            self._annotation_label.config(text="")

        # ── Run pattern/signal detection on the VISIBLE intraday window ────────
        try:
            intra_detected    = detect_patterns(df) if len(df) >= 40 else []
            intra_quant       = compute_quant_signals(df) if len(df) >= 20 else {}
            intra_brooks      = detect_brooks_signals(df) if len(df) >= 10 else []
            intra_streets     = detect_street_smarts(df) if len(df) >= 10 else []
        except Exception:
            intra_detected = []; intra_quant = {}; intra_brooks = []; intra_streets = []

        # Overlay intraday-detected necklines/stops/targets (green = intraday signals)
        for pat in intra_detected[:3]:
            if 'neckline' in pat:
                nl = pat['neckline']
                ax.axhline(y=nl, color='#27ae60', linestyle='-',
                           alpha=0.9, linewidth=1.8,
                           label=f"Intra Neckline: {nl:.2f}")
                overlay_lines.append((f"INTRA ENTRY ({pat.get('name','')[:12]})", nl, '#27ae60'))
            if 'pattern_low' in pat:
                sl = pat['pattern_low'] * 0.99
                ax.axhline(y=sl, color='#c0392b', linestyle=':',
                           alpha=0.9, linewidth=1.2,
                           label=f"Intra Stop: {sl:.2f}")
                overlay_lines.append(('INTRA STOP', sl, '#c0392b'))

        # IBS signal on intraday last bar
        last = df.iloc[-1]
        rng  = last['High'] - last['Low']
        ibs  = (last['Close'] - last['Low']) / rng if rng > 0 else 0.5
        ibs_txt = f"IBS={ibs:.2f} "
        if ibs <= 0.20:    ibs_txt += "▲ OVERSOLD"
        elif ibs >= 0.80:  ibs_txt += "▼ OVERBOUGHT"
        else:              ibs_txt += "◆ NEUTRAL"

        n_pat = len(intra_detected)
        n_ss  = len(intra_streets)
        ax.set_title(
            f"Intraday Chart  —  {ibs_txt}  —  {len(df)} bars  |  "            f"{n_pat} pattern(s)  {n_ss} SS signal(s)",
            color='#e0e0e0', fontsize=9, pad=6)
        ax.tick_params(colors='#aaaaaa', labelsize=7)
        for spine in ax.spines.values():
            spine.set_edgecolor('#333344')

        # X labels every N bars — show time portion of datetime
        step = max(1, len(dates) // 12)
        labels = df['Date'].astype(str).values
        ax.set_xticks(list(dates)[::step])
        ax.set_xticklabels([str(labels[i])[-8:] for i in range(0, len(dates), step)],
                           rotation=30, ha='right', fontsize=6, color='#aaaaaa')
        ax.set_ylabel('Price', color='#aaaaaa', fontsize=8)
        ax.yaxis.label.set_color('#aaaaaa')

        if overlay_lines:
            ax.legend(loc='upper left', fontsize=6, facecolor='#0d1117',
                      labelcolor='white', framealpha=0.85, edgecolor='#555',
                      ncol=2)

        # Push intraday results to the right panel if intraday tab is active
        if getattr(self, '_active_tab', 'daily') == 'intraday':
            self.detected       = intra_detected
            self.quant_signals  = intra_quant
            self.brooks_signals = intra_brooks
            self.street_smarts  = intra_streets
            self._refresh_results_panel()

        self.fig_intra.tight_layout()
        self.canvas_intra.draw()

    def _refresh_results_panel(self):
        """Re-trigger the results panel refresh with the latest detected signals."""
        try:
            self._refresh_signal_view()
        except Exception:
            pass

    def _setup_intraday_crosshair(self):
        """Bind crosshair to intraday canvas."""
        # Also bind mousewheel to scroll through intraday bars
        def _on_wheel(event):
            if self.df_intra is None:
                return
            # On Windows event.delta; on Linux event.num
            delta = 0
            if hasattr(event, 'delta') and event.delta:
                delta = -1 if event.delta > 0 else 1
            elif hasattr(event, 'num'):
                delta = -1 if event.num == 4 else 1
            step = max(5, self._intra_window_size // 8)
            self._intra_offset = max(0,
                min(len(self.df_intra) - self._intra_window_size,
                    self._intra_offset + delta * step))
            self._draw_intraday_chart()

        try:
            w = self.canvas_intra.get_tk_widget()
            w.bind('<MouseWheel>', _on_wheel)
            w.bind('<Button-4>',   _on_wheel)
            w.bind('<Button-5>',   _on_wheel)
        except Exception:
            pass
        if self._cid_move_intra is not None:
            try: self.canvas_intra.mpl_disconnect(self._cid_move_intra)
            except Exception: pass
        if self._cid_leave_intra is not None:
            try: self.canvas_intra.mpl_disconnect(self._cid_leave_intra)
            except Exception: pass
        self._cid_move_intra  = self.canvas_intra.mpl_connect(
            'motion_notify_event', self._on_intra_move)
        self._cid_leave_intra = self.canvas_intra.mpl_connect(
            'axes_leave_event',    self._on_intra_leave)

    def _on_intra_leave(self, event):
        for attr in ('_ch_h_intra','_ch_v_intra','_ch_xb_intra','_ch_yb_intra'):
            a = getattr(self, attr, None)
            if a:
                try: a.remove()
                except Exception: pass
            setattr(self, attr, None)
        self.canvas_intra.draw_idle()
        self._intra_xhbar.config(
            text="  Move mouse over intraday chart",
            fg='#777')

    def _on_intra_move(self, event):
        if self.df_intra is None or event.inaxes is None:
            return
        ax = event.inaxes
        x, y = event.xdata, event.ydata
        if x is None or y is None:
            return
        for attr in ('_ch_h_intra','_ch_v_intra','_ch_xb_intra','_ch_yb_intra'):
            a = getattr(self, attr, None)
            if a:
                try: a.remove()
                except Exception: pass
            setattr(self, attr, None)

        self._ch_h_intra = ax.axhline(y=y, color='#ffffff',
                                      linewidth=0.7, linestyle='--',
                                      alpha=0.6, zorder=10)
        self._ch_v_intra = ax.axvline(x=x, color='#ffffff',
                                      linewidth=0.7, linestyle='--',
                                      alpha=0.6, zorder=10)
        self._ch_yb_intra = ax.text(
            ax.get_xlim()[0], y, f' {y:,.2f} ',
            color='#0d1117', fontsize=8, fontfamily='monospace',
            verticalalignment='center', horizontalalignment='left',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='#1abc9c',
                      edgecolor='#1abc9c', alpha=0.95), zorder=11)

        bar_idx = max(0, min(int(round(x)), len(self.df_intra) - 1))
        date_str = str(self.df_intra['Date'].iloc[bar_idx])[-8:]
        self._ch_xb_intra = ax.text(
            x, ax.get_ylim()[0], f' {date_str} ',
            color='#0d1117', fontsize=8, fontfamily='monospace',
            verticalalignment='bottom', horizontalalignment='center',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='#1abc9c',
                      edgecolor='#1abc9c', alpha=0.95), zorder=11)

        row  = self.df_intra.iloc[bar_idx]
        o_, h_, l_, c_ = row['Open'], row['High'], row['Low'], row['Close']
        chg  = c_ - o_
        pct  = chg / o_ * 100 if o_ != 0 else 0
        sym  = '▲' if chg >= 0 else '▼'
        col  = '#2ecc71' if chg >= 0 else '#e74c3c'
        rng  = h_ - l_
        ibs  = (c_ - l_) / rng if rng > 0 else 0.5
        info = (f"  ⏱ {str(self.df_intra['Date'].iloc[bar_idx])[-16:]}  "
                f"O:{o_:,.2f} H:{h_:,.2f} L:{l_:,.2f} C:{c_:,.2f}  "
                f"{sym}{abs(chg):,.2f}({pct:+.2f}%)  IBS:{ibs:.2f}")
        self._intra_xhbar.config(text=info, fg=col)
        self.canvas_intra.draw_idle()

    # ─────────────────────────────────────────────────────────────────────────
    #  DRAWING TOOLS
    # ─────────────────────────────────────────────────────────────────────────

    def _set_draw_mode(self, mode):
        """Activate a drawing mode and update button styles."""
        self._draw_mode.set(mode)
        # Disconnect nav toolbar zoom/pan when in draw mode
        try:
            if mode != 'none':
                self._nav_toolbar.mode = ''  # deactivate zoom/pan
        except Exception:
            pass
        # Update button colors
        color_map = {'hline': '#2980b9', 'trendline': '#27ae60', 'rect': '#8e44ad'}
        for m, btn in self._draw_btns.items():
            if m == 'clear':
                continue
            if m == mode:
                btn.config(bg=color_map.get(m, '#555'), fg='white',
                           relief='solid', bd=2)
            else:
                btn.config(bg='#e0e0e0', fg='#333', relief='flat', bd=0)

        if mode != 'none':
            self.canvas.get_tk_widget().config(cursor='crosshair')
            # Bind drawing events
            if not hasattr(self, '_draw_cid_press') or not self._draw_cid_press:
                self._draw_cid_press = self.canvas.mpl_connect(
                    'button_press_event', self._on_draw_press)
                self._draw_cid_release = self.canvas.mpl_connect(
                    'button_release_event', self._on_draw_release)
                self._draw_cid_drag = self.canvas.mpl_connect(
                    'motion_notify_event', self._on_draw_drag)
        else:
            self.canvas.get_tk_widget().config(cursor='arrow')
            self._unbind_draw_events()

    def _unbind_draw_events(self):
        for attr in ('_draw_cid_press', '_draw_cid_release', '_draw_cid_drag'):
            cid = getattr(self, attr, None)
            if cid:
                try:
                    self.canvas.mpl_disconnect(cid)
                except Exception:
                    pass
                setattr(self, attr, None)

    def _clear_drawings(self):
        """Remove all user-drawn lines from the chart."""
        for artist in self._draw_lines:
            try:
                artist.remove()
            except Exception:
                pass
        self._draw_lines.clear()
        if self._draw_temp:
            try:
                self._draw_temp.remove()
            except Exception:
                pass
            self._draw_temp = None
        self.canvas.draw_idle()
        # Reset mode
        self._draw_mode.set('none')
        for m, btn in self._draw_btns.items():
            if m != 'clear':
                btn.config(bg='#e0e0e0', fg='#333', relief='flat', bd=0)
        self.canvas.get_tk_widget().config(cursor='arrow')
        self._unbind_draw_events()

    def _on_draw_press(self, event):
        if event.inaxes is None or event.button != 1:
            return
        mode = self._draw_mode.get()
        ax   = event.inaxes
        x, y = event.xdata, event.ydata

        if mode == 'hline':
            # Draw horizontal line immediately
            line, = ax.plot(ax.get_xlim(), [y, y],
                            color='#2980b9', linestyle='--',
                            linewidth=1.5, alpha=0.85, zorder=10)
            ax.text(ax.get_xlim()[1] * 0.98, y, f' {y:,.2f}',
                    color='#2980b9', fontsize=7, va='bottom',
                    fontfamily='monospace')
            self._draw_lines.append(line)
            self.canvas.draw_idle()

        elif mode in ('trendline', 'rect'):
            self._draw_start = (x, y, ax)

    def _on_draw_drag(self, event):
        if event.inaxes is None:
            return
        mode = self._draw_mode.get()
        if mode not in ('trendline', 'rect'):
            return
        if not self._draw_start:
            return

        x0, y0, ax = self._draw_start
        x1, y1 = event.xdata, event.ydata
        if x1 is None or y1 is None:
            return

        # Remove old temp line
        if self._draw_temp:
            try:
                self._draw_temp.remove()
            except Exception:
                pass
            self._draw_temp = None

        if mode == 'trendline':
            line, = ax.plot([x0, x1], [y0, y1],
                            color='#27ae60', linewidth=1.5,
                            linestyle='-', alpha=0.75, zorder=10)
            self._draw_temp = line

        elif mode == 'rect':
            from matplotlib.patches import Rectangle
            w = x1 - x0
            h = y1 - y0
            rect = Rectangle((min(x0, x1), min(y0, y1)),
                              abs(w), abs(h),
                              linewidth=1.5, edgecolor='#8e44ad',
                              facecolor='#8e44ad', alpha=0.08,
                              zorder=9)
            ax.add_patch(rect)
            self._draw_temp = rect

        self.canvas.draw_idle()

    def _on_draw_release(self, event):
        if not self._draw_start:
            return
        mode = self._draw_mode.get()
        if event.inaxes is None:
            self._draw_start = None
            return

        x0, y0, ax = self._draw_start
        x1, y1 = event.xdata or x0, event.ydata or y0

        if mode == 'trendline':
            if self._draw_temp:
                self._draw_lines.append(self._draw_temp)
                self._draw_temp = None
                # Add price labels at endpoints
                ax.text(x1, y1, f' {y1:,.2f}', color='#27ae60',
                        fontsize=7, va='bottom', fontfamily='monospace')
        elif mode == 'rect':
            if self._draw_temp:
                self._draw_lines.append(self._draw_temp)
                self._draw_temp = None

        self._draw_start = None
        self.canvas.draw_idle()

    # ─────────────────────────────────────────────────────────────────────────
    #  CROSSHAIR (daily chart)
    # ─────────────────────────────────────────────────────────────────────────

    def _setup_crosshair(self):
        """Bind mouse events to canvas for crosshair display."""
        # Disconnect old events if they exist
        if self._cid_move  is not None:
            try: self.canvas.mpl_disconnect(self._cid_move)
            except Exception: pass
        if self._cid_leave is not None:
            try: self.canvas.mpl_disconnect(self._cid_leave)
            except Exception: pass

        self._cid_move  = self.canvas.mpl_connect('motion_notify_event',
                                                   self._on_mouse_move)
        self._cid_leave = self.canvas.mpl_connect('axes_leave_event',
                                                   self._on_mouse_leave)

    def _on_mouse_leave(self, event):
        """Hide crosshair when mouse leaves the axes."""
        self._remove_crosshair()
        self.canvas.draw_idle()
        self._crosshair_bar.config(
            text="  Move mouse over chart to see OHLC values",
            fg='#555555')

    def _remove_crosshair(self):
        """Remove all crosshair artists from the chart."""
        for attr in ('_crosshair_h', '_crosshair_v',
                     '_crosshair_xbox', '_crosshair_ybox',
                     '_crosshair_ohlc'):
            artist = getattr(self, attr, None)
            if artist is not None:
                try:
                    artist.remove()
                except Exception:
                    pass
                setattr(self, attr, None)

    def _on_mouse_move(self, event):
        """Draw crosshair lines and display OHLC info on mouse move."""
        if self.df is None:
            return
        if event.inaxes is None:
            return

        ax = event.inaxes
        x  = event.xdata
        y  = event.ydata
        if x is None or y is None:
            return

        # Remove old crosshair artists
        self._remove_crosshair()

        # ── Draw crosshair lines ──────────────────────────────────────────
        self._crosshair_h = ax.axhline(
            y=y, color='#ffffff', linewidth=0.7,
            linestyle='--', alpha=0.6, zorder=10)

        self._crosshair_v = ax.axvline(
            x=x, color='#ffffff', linewidth=0.7,
            linestyle='--', alpha=0.6, zorder=10)

        # ── Price label on Y axis ────────────────────────────────────────
        self._crosshair_ybox = ax.text(
            ax.get_xlim()[0], y,
            f' {y:,.2f} ',
            color='#0d1117',
            fontsize=8,
            fontfamily='monospace',
            verticalalignment='center',
            horizontalalignment='left',
            bbox=dict(boxstyle='round,pad=0.2',
                      facecolor='#f1c40f',
                      edgecolor='#f1c40f',
                      alpha=0.95),
            zorder=11
        )

        # ── Date label on X axis ─────────────────────────────────────────
        bar_idx = int(round(x))
        bar_idx = max(0, min(bar_idx, len(self.df) - 1))
        date_str = str(self.df['Date'].iloc[bar_idx])[:10]

        self._crosshair_xbox = ax.text(
            x, ax.get_ylim()[0],
            f' {date_str} ',
            color='#0d1117',
            fontsize=8,
            fontfamily='monospace',
            verticalalignment='bottom',
            horizontalalignment='center',
            bbox=dict(boxstyle='round,pad=0.2',
                      facecolor='#f1c40f',
                      edgecolor='#f1c40f',
                      alpha=0.95),
            zorder=11
        )

        # ── OHLC values for the hovered bar ─────────────────────────────
        row  = self.df.iloc[bar_idx]
        o_   = row['Open']
        h_   = row['High']
        l_   = row['Low']
        c_   = row['Close']
        chg  = c_ - o_
        pct  = chg / o_ * 100 if o_ != 0 else 0
        chg_sym   = '▲' if chg >= 0 else '▼'
        bar_color = '#2ecc71' if chg >= 0 else '#e74c3c'

        # Volume if available
        vol_str = ''
        if 'Volume' in self.df.columns:
            vol = row['Volume']
            if vol >= 1_000_000:
                vol_str = f"  Vol: {vol/1_000_000:.2f}M"
            elif vol >= 1_000:
                vol_str = f"  Vol: {vol/1_000:.1f}K"
            else:
                vol_str = f"  Vol: {int(vol)}"

        # Update info bar below chart
        info = (f"  📅 {date_str}    "
                f"O: {o_:,.2f}   "
                f"H: {h_:,.2f}   "
                f"L: {l_:,.2f}   "
                f"C: {c_:,.2f}   "
                f"{chg_sym} {abs(chg):,.2f} ({pct:+.2f}%)"
                f"{vol_str}")
        self._crosshair_bar.config(text=info, fg=bar_color)

        self.canvas.draw_idle()

    # ─────────────────────────────────────────────────────────────────────────
    #  SIGNAL TYPE SELECTOR — refreshes chart + listbox for selected mode
    # ─────────────────────────────────────────────────────────────────────────

    def _refresh_signal_view(self):
        """Called when user selects All / Bulkowski / Brooks PA / Quant."""
        mode = self._signal_mode.get()

        # ── Update chart to show only selected type ───────────────────────
        if self.df is not None:
            bk = self.detected       if mode in ('all', 'bulkowski')    else []
            br = getattr(self, 'brooks_signals',  []) if mode in ('all', 'brooks')      else []
            qt = getattr(self, 'quant_signals',   []) if mode in ('all', 'quant')       else []
            ss = getattr(self, 'street_smarts',   []) if mode in ('all', 'streetsmarts') else []

            draw_chart_unified(self.fig, self.df, bk, qt, br, ss)
            self.canvas.draw_idle()

        # ── Refresh the listbox ───────────────────────────────────────────
        self.pattern_listbox.delete(0, tk.END)
        mode = self._signal_mode.get()

        if mode in ('all', 'bulkowski'):
            pats = getattr(self, 'detected', [])
            if pats:
                if mode == 'all':
                    self.pattern_listbox.insert(tk.END,
                        f" ─── BULKOWSKI ({len(pats)}) ───────────────")
                for p in pats:
                    d  = "▲" if "BULL" in p['direction'] else ("▼" if "BEAR" in p['direction'] else "◆")
                    comp = p.get('completion', {})
                    st = comp.get('status', '')
                    ic = '✅' if 'CONFIRMED' in st else ('⚡' if 'IMMINENT' in st else '🔄')
                    self.pattern_listbox.insert(tk.END,
                        f" {d} {p['name'][:24]:<24} {p['confidence']:3.0f}% {ic}")
            elif mode == 'bulkowski':
                self.pattern_listbox.insert(tk.END, "  No Bulkowski patterns detected")

        if mode in ('all', 'brooks'):
            sigs = getattr(self, 'brooks_signals', [])
            if sigs:
                if mode == 'all':
                    self.pattern_listbox.insert(tk.END,
                        f" ─── BROOKS PA ({len(sigs)}) ──────────────")
                for s in sigs:
                    self.pattern_listbox.insert(tk.END,
                        f" {s['icon']} {s['name'][8:][:24]:<24} {s['confidence']:3.0f}%")
            elif mode == 'brooks':
                self.pattern_listbox.insert(tk.END, "  No Brooks PA signals detected")

        if mode in ('all', 'quant'):
            qsigs = getattr(self, 'quant_signals', [])
            if mode == 'quant' and qsigs:
                for s in qsigs:
                    ic = '▲' if s['color'] == '#2ecc71' else ('▼' if s['color'] == '#e74c3c' else '◆')
                    self.pattern_listbox.insert(tk.END,
                        f" {ic} {s['name'][:28]:<28}  {s['signal'][:12]}")
            elif mode == 'all':
                q_bull = sum(1 for s in qsigs if s['color'] == '#2ecc71')
                q_bear = sum(1 for s in qsigs if s['color'] == '#e74c3c')
                self.pattern_listbox.insert(tk.END,
                    f" ─── QUANT: ▲{q_bull} bullish  ▼{q_bear} bearish ───")
            elif mode == 'quant':
                self.pattern_listbox.insert(tk.END, "  Run Detect first to compute quant signals")

        if mode in ('all', 'streetsmarts'):
            ss_sigs = getattr(self, 'street_smarts', [])
            if ss_sigs:
                if mode == 'all':
                    self.pattern_listbox.insert(tk.END,
                        f" ─── STREET SMARTS ({len(ss_sigs)}) ─────────")
                for s in ss_sigs:
                    self.pattern_listbox.insert(tk.END,
                        f" {s['icon']} {s['name'][15:][:24]:<24} {s['confidence']:3.0f}%")
            elif mode == 'streetsmarts':
                self.pattern_listbox.insert(tk.END, "  No Street Smarts signals detected")

        # Auto-select first real entry
        if self.pattern_listbox.size() > 0:
            # Skip section header lines (they start with " ─")
            for i in range(self.pattern_listbox.size()):
                item = self.pattern_listbox.get(i)
                if not item.startswith(' ─'):
                    self.pattern_listbox.selection_set(i)
                    self._on_pattern_select(None)
                    break

    def _btn(self, parent, text, command, color):
        return tk.Button(parent, text=text, command=command,
                         bg=color, fg='white', relief='flat',
                         font=('Consolas', 9, 'bold'),
                         padx=10, pady=5, cursor='hand2',
                         activebackground=color, activeforeground='white')

    def _show_welcome(self):
        self.detail_text.config(state='normal')
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.insert(tk.END, "BULKOWSKI CHART PATTERN ANALYZER\n", 'header')
        self.detail_text.insert(tk.END, "─" * 45 + "\n", 'divider')
        self.detail_text.insert(tk.END, "\nBased on: Encyclopedia of Chart Patterns\n", 'label')
        self.detail_text.insert(tk.END, "Thomas N. Bulkowski, 2nd Ed. (2005)\n\n", 'label')
        self.detail_text.insert(tk.END, "Database: 38,500+ chart pattern samples\n", 'value')
        self.detail_text.insert(tk.END, "Kakushadze Quant Signals: 18 signals\n", 'value')
        self.detail_text.insert(tk.END, "Patterns included: 53 chart patterns\n\n", 'value')
        self.detail_text.insert(tk.END, "HOW TO START:\n", 'header')
        self.detail_text.insert(tk.END, "1. Click 'Load CSV Data'\n", 'rule')
        self.detail_text.insert(tk.END, "2. Select your OHLCV CSV file\n", 'rule')
        self.detail_text.insert(tk.END, "3. Click 'Detect Patterns'\n", 'rule')
        self.detail_text.insert(tk.END, "4. Select a pattern from the list\n", 'rule')
        self.detail_text.insert(tk.END, "5. View entry, stop, target, stats\n\n", 'rule')
        self.detail_text.insert(tk.END, "CSV COLUMNS NEEDED:\n", 'header')
        self.detail_text.insert(tk.END, "Date, Open, High, Low, Close, Volume\n", 'value')
        self.detail_text.config(state='disabled')

    def _load_csv(self):
        filepath = filedialog.askopenfilename(
            title="Select OHLCV CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not filepath:
            return
        try:
            df = pd.read_csv(filepath)
            df.columns = [c.strip().capitalize() for c in df.columns]
            # Flexible column mapping
            col_map = {}
            for col in df.columns:
                cl = col.lower()
                if 'date' in cl or 'time' in cl: col_map[col] = 'Date'
                elif cl == 'open' or cl == 'o': col_map[col] = 'Open'
                elif cl == 'high' or cl == 'h': col_map[col] = 'High'
                elif cl == 'low'  or cl == 'l': col_map[col] = 'Low'
                elif cl == 'close' or cl == 'c': col_map[col] = 'Close'
                elif 'vol' in cl: col_map[col] = 'Volume'
            df.rename(columns=col_map, inplace=True)
            required = ['Open', 'High', 'Low', 'Close']
            for r in required:
                if r not in df.columns:
                    raise ValueError(f"Missing column: {r}. Found: {list(df.columns)}")
            for col in required:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            df.dropna(subset=required, inplace=True)
            if 'Date' not in df.columns:
                df['Date'] = range(len(df))
            # Fix: sort oldest → newest (handles CSVs downloaded from NSE/Zerodha/Upstox)
            try:
                df['Date'] = pd.to_datetime(df['Date'])
                df.sort_values('Date', ascending=True, inplace=True)
                df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
            except Exception:
                pass  # If date parsing fails, keep original order
            df.reset_index(drop=True, inplace=True)
            self.df = df
            self.status_var.set(f"✅ Loaded: {filepath.split('/')[-1]} — {len(df)} bars ({df['Date'].iloc[0]} to {df['Date'].iloc[-1]})")
            # Draw blank chart
            draw_chart(self.fig, self.df, [])
            self.canvas.draw()
            self._setup_crosshair()
            self._switch_tab('daily')
            messagebox.showinfo("Data Loaded",
                f"✅ {len(df)} bars loaded successfully.\n\nClick 'Detect Patterns' to analyze.")
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load file:\n{str(e)}\n\nCheck that your CSV has Date, Open, High, Low, Close columns.")

    def _detect(self):
        if self.df is None:
            messagebox.showwarning("No Data", "Please load a CSV file first.")
            return
        self.status_var.set("🔍 Running all detectors simultaneously...")
        self.root.update()
        try:
            self.detected       = detect_patterns(self.df)
            self.quant_signals  = compute_quant_signals(self.df)
            self.brooks_signals = detect_brooks_signals(self.df)
            self.street_smarts  = detect_street_smarts(self.df)
            for p in self.detected:
                if 'completion' not in p:
                    p['completion'] = get_completion_status(p, self.df)
            draw_chart_unified(self.fig, self.df, self.detected,
                               self.quant_signals, self.brooks_signals,
                               self.street_smarts)
            self.canvas.draw()
            self._setup_crosshair()
            if self.df_intra is not None:
                self._draw_intraday_chart()
            self.status_var.set(
                f"✅ Bulkowski:{len(self.detected)}  Brooks:{len(self.brooks_signals)}  "
                f"Quant:{len(self.quant_signals)}  StreetSmarts:{len(self.street_smarts)}"
                f"  — Use selector to filter signal types")
            # Refresh listbox according to current mode selection
            self._refresh_signal_view()
        except Exception as e:
            import traceback
            messagebox.showerror("Detection Error", f"Error:\n{str(e)}\n\n{traceback.format_exc()[:400]}")
            self.status_var.set(f"❌ Error: {str(e)}")

    def _on_pattern_select(self, event):
        sel = self.pattern_listbox.curselection()
        if not sel:
            return
        idx  = sel[0]
        item = self.pattern_listbox.get(idx)

        # Skip section header dividers
        if item.startswith(' ─') or item.startswith('  No ') or item.startswith('  Run '):
            return

        mode = self._signal_mode.get()

        # ── Quant mode: show quant signal detail ──────────────────────────
        if mode == 'quant':
            qsigs = getattr(self, 'quant_signals', [])
            if idx < len(qsigs):
                self._show_quant_detail_inline(qsigs[idx])
            return

        # ── Work out which list section the selected row belongs to ───────
        # Count header rows to map listbox index → correct data list
        bk_pats = getattr(self, 'detected', [])
        br_sigs = getattr(self, 'brooks_signals', [])

        if mode == 'bulkowski':
            if idx < len(bk_pats):
                self._show_pattern_detail(bk_pats[idx])
            return

        if mode == 'streetsmarts':
            ss = getattr(self, 'street_smarts', [])
            if idx < len(ss):
                self._show_street_smarts_inline(ss[idx])
            return

        # mode == 'all': figure out section from the item content
        # Build a flat map of listbox index → (type, data_object)
        flat_map = {}
        lb_i = 0
        if bk_pats:
            flat_map[lb_i] = ('header', None); lb_i += 1
            for p in bk_pats:
                flat_map[lb_i] = ('bulkowski', p); lb_i += 1
        if br_sigs:
            flat_map[lb_i] = ('header', None); lb_i += 1
            for s in br_sigs:
                flat_map[lb_i] = ('brooks', s); lb_i += 1
        # quant summary row
        flat_map[lb_i] = ('header', None); lb_i += 1
        ss_sigs = getattr(self, 'street_smarts', [])
        if ss_sigs:
            flat_map[lb_i] = ('header', None); lb_i += 1
            for s in ss_sigs:
                flat_map[lb_i] = ('streetsmarts', s); lb_i += 1

        entry = flat_map.get(idx)
        if entry is None or entry[0] == 'header':
            return
        sig_type, data = entry
        if sig_type == 'bulkowski':
            self._show_pattern_detail(data)
        elif sig_type == 'brooks':
            self._show_brooks_signal_inline(data)
        elif sig_type == 'streetsmarts':
            self._show_street_smarts_inline(data)

    def _show_quant_detail_inline(self, sig):
        """Show a quant signal detail in the main detail panel."""
        self.detail_text.config(state='normal')
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.insert(tk.END, f"\n{sig['name'].upper()}\n", 'header')
        self.detail_text.insert(tk.END, f"Source: {sig['source']}\n", 'rule')
        self.detail_text.insert(tk.END, "─" * 40 + "\n\n", 'divider')
        s_tag = 'bullish' if sig['color'] == '#2ecc71' else ('bearish' if sig['color'] == '#e74c3c' else 'neutral')
        self.detail_text.insert(tk.END, f"SIGNAL:  {sig['icon']} {sig['signal']}\n\n", s_tag)
        self.detail_text.insert(tk.END, f"VALUE:\n  {sig['value']}\n\n", 'value')
        self.detail_text.insert(tk.END, "─── EXPLANATION ─────────────────────────\n", 'divider')
        self.detail_text.insert(tk.END, f"{sig['desc']}\n\n", 'value')
        self.detail_text.insert(tk.END, "─── TRADING RULES ───────────────────────\n", 'divider')
        for line in sig['trade_rule'].split('\n'):
            self.detail_text.insert(tk.END, f"  {line}\n", 'rule')
        self.detail_text.config(state='disabled')

    def _show_brooks_signal_inline(self, sig):
        """Show a Brooks PA signal detail in the main detail panel."""
        self.detail_text.config(state='normal')
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.insert(tk.END, f"\n{sig['name'].upper()}\n", 'header')
        self.detail_text.insert(tk.END, f"Source: {sig['source']}\n", 'rule')
        self.detail_text.insert(tk.END, "─" * 40 + "\n\n", 'divider')
        s_tag = 'bullish' if '▲' in sig['signal'] else ('bearish' if '▼' in sig['signal'] else 'neutral')
        conf = sig.get('confidence', 0)
        cb   = "█" * int(conf/10) + "░" * (10 - int(conf/10))
        self.detail_text.insert(tk.END, f"SIGNAL:     {sig['signal']}\n", s_tag)
        self.detail_text.insert(tk.END, f"CONFIDENCE: {conf}%  [{cb}]\n\n", 'label')
        self.detail_text.insert(tk.END, f"VALUE:\n  {sig['value']}\n\n", 'value')
        self.detail_text.insert(tk.END, "─── TRADING PLAN ────────────────────────\n", 'divider')
        self.detail_text.insert(tk.END, "▸ ENTRY:\n", 'entry')
        self.detail_text.insert(tk.END, f"  {sig['entry']}\n\n", 'value')
        self.detail_text.insert(tk.END, "▸ STOP:\n", 'stop')
        self.detail_text.insert(tk.END, f"  {sig['stop']}\n\n", 'value')
        self.detail_text.insert(tk.END, "▸ TARGET:\n", 'target')
        self.detail_text.insert(tk.END, f"  {sig['target']}\n\n", 'value')

        # R:R calculation if prices available
        try:
            import re as _re
            def ep(s):
                nums = _re.findall(r'\d+\.?\d*', str(s))
                return float(nums[0]) if nums else None
            ev = ep(sig['entry']); sv = ep(sig['stop']); tv = ep(sig['target'])
            if ev and sv and tv:
                rr = calc_rr(ev, sv, tv)
                if rr:
                    self.detail_text.insert(tk.END, "─── R:R CALCULATOR ──────────────────────\n", 'divider')
                    self.detail_text.insert(tk.END, f"  Risk:    {rr['risk']:.2f}\n", 'stop')
                    self.detail_text.insert(tk.END, f"  Reward:  {rr['reward']:.2f}\n", 'entry')
                    rr_tag = 'entry' if rr['rr'] >= 2 else ('warning' if rr['rr'] >= 1 else 'stop')
                    self.detail_text.insert(tk.END, f"  R:R:     1 : {rr['rr']:.1f}  Grade: {rr['grade']}\n", rr_tag)
                    self.detail_text.insert(tk.END, f"  {rr['advice']}\n\n", 'value')
        except Exception:
            pass

        self.detail_text.insert(tk.END, "─── EXPLANATION ─────────────────────────\n", 'divider')
        self.detail_text.insert(tk.END, f"{sig['desc']}\n\n", 'value')

        # Lookup in BROOKS_DB for extra detail
        name_key = sig['name'][8:] if sig['name'].startswith('Brooks: ') else sig['name']
        for key in BROOKS_DB:
            if any(w in key for w in name_key.split()[:2]):
                db = BROOKS_DB[key]
                self.detail_text.insert(tk.END, "─── FIRST PRINCIPLE ─────────────────────\n", 'divider')
                self.detail_text.insert(tk.END, f"{db['first_principle']}\n\n", 'rule')
                self.detail_text.insert(tk.END, "─── IDENTIFICATION CHECKLIST ────────────\n", 'divider')
                for item in db['identification']:
                    self.detail_text.insert(tk.END, f"  ✓ {item}\n", 'rule')
                self.detail_text.insert(tk.END, f"\n{db['edge']}\n", 'best')
                break
        self.detail_text.config(state='disabled')

    def _show_pattern_detail(self, pat):
        # Get Bulkowski database entry
        db_match = None
        for key in PATTERNS_DB:
            if pat['name'] in key or key in pat['name']:
                db_match = PATTERNS_DB[key]
                break
        # Also try partial match
        if db_match is None:
            for key in PATTERNS_DB:
                if any(word in key for word in pat['name'].split()[:2]):
                    db_match = PATTERNS_DB[key]
                    break

        self.detail_text.config(state='normal')
        self.detail_text.delete(1.0, tk.END)

        # Header
        self.detail_text.insert(tk.END, f"\n{'─'*45}\n", 'divider')
        self.detail_text.insert(tk.END, f" {pat['name'].upper()}\n", 'header')
        self.detail_text.insert(tk.END, f"{'─'*45}\n\n", 'divider')

        # Confidence
        conf = pat['confidence']
        conf_bar = "█" * int(conf / 10) + "░" * (10 - int(conf / 10))
        self.detail_text.insert(tk.END, f"CONFIDENCE:  {conf:.0f}%  [{conf_bar}]\n", 'header')

        # Direction
        dir_tag = 'bullish' if 'BULL' in pat['direction'] else ('bearish' if 'BEAR' in pat['direction'] else 'neutral')
        dir_icon = "▲ BULLISH" if 'BULL' in pat['direction'] else ("▼ BEARISH" if 'BEAR' in pat['direction'] else "◆ NEUTRAL")
        self.detail_text.insert(tk.END, f"DIRECTION:   {dir_icon}\n\n", dir_tag)

        # ── PATTERN COMPLETION STATUS ──────────────────────────────────────
        comp = pat.get('completion', {})
        if comp:
            self.detail_text.insert(tk.END, "─── PATTERN COMPLETION STATUS ──────────\n", 'divider')
            status = comp.get('status', '')
            pct    = comp.get('pct', 0)
            desc   = comp.get('desc', '')
            # Progress bar
            filled = int(pct / 10)
            prog   = "█" * filled + "░" * (10 - filled)
            if 'CONFIRMED' in status:
                self.detail_text.insert(tk.END, f"{status}\n", 'entry')
            elif 'IMMINENT' in status:
                self.detail_text.insert(tk.END, f"{status}\n", 'target')
            else:
                self.detail_text.insert(tk.END, f"{status}\n", 'neutral')
            self.detail_text.insert(tk.END,
                f"Progress:    {pct}%  [{prog}]\n\n", 'label')
            self.detail_text.insert(tk.END, f"{desc}\n\n", 'value')

        # ── TRADING PLAN ──
        self.detail_text.insert(tk.END, "─── TRADING PLAN ───────────────────────\n", 'divider')

        self.detail_text.insert(tk.END, "▸ ENTRY:  ", 'entry')
        self.detail_text.insert(tk.END, f"{pat['entry']}\n\n", 'value')

        self.detail_text.insert(tk.END, "▸ STOP:   ", 'stop')
        self.detail_text.insert(tk.END, f"{pat['stop']}\n\n", 'value')

        self.detail_text.insert(tk.END, "▸ TARGET: ", 'target')
        self.detail_text.insert(tk.END, f"{pat['target']}\n\n", 'value')

        # ── R:R CALCULATOR ─────────────────────────────────────────────────
        try:
            # Parse numeric values from strings like "Close above neckline: 245.50"
            import re
            def extract_price(s):
                nums = re.findall(r'\d+\.?\d*', str(s))
                return float(nums[0]) if nums else None

            entry_price  = extract_price(pat['entry'])
            stop_price   = extract_price(pat['stop'])
            target_price = extract_price(pat['target'])

            if entry_price and stop_price and target_price:
                rr_data = calc_rr(entry_price, stop_price, target_price)
                if rr_data:
                    self.detail_text.insert(tk.END,
                        "─── RISK : REWARD CALCULATOR ───────────\n", 'divider')
                    self.detail_text.insert(tk.END,
                        f"  Entry Price     {entry_price:>10.2f}\n", 'label')
                    self.detail_text.insert(tk.END,
                        f"  Stop Price      {stop_price:>10.2f}\n", 'label')
                    self.detail_text.insert(tk.END,
                        f"  Target Price    {target_price:>10.2f}\n\n", 'label')
                    self.detail_text.insert(tk.END,
                        f"  Risk (per unit) {rr_data['risk']:>10.2f}\n", 'stop')
                    self.detail_text.insert(tk.END,
                        f"  Reward          {rr_data['reward']:>10.2f}\n", 'entry')
                    rr_val = rr_data['rr']
                    self.detail_text.insert(tk.END,
                        f"  R:R Ratio       {rr_val:>10.2f}  (1 : {rr_val:.1f})\n\n",
                        'entry' if rr_val >= 2 else ('warning' if rr_val >= 1 else 'stop'))
                    grade_tag = 'entry' if 'EXCELLENT' in rr_data['grade'] or rr_data['grade'].startswith('A') else \
                                ('target' if rr_data['grade'].startswith('B') else \
                                ('warning' if rr_data['grade'].startswith('C') else 'stop'))
                    self.detail_text.insert(tk.END,
                        f"  Grade:  {rr_data['grade']}\n", grade_tag)
                    self.detail_text.insert(tk.END,
                        f"  {rr_data['advice']}\n\n", 'value')

                    # Position sizing hint
                    self.detail_text.insert(tk.END,
                        "─── POSITION SIZING HINT ───────────────\n", 'divider')
                    for capital in [10000, 50000, 100000]:
                        risk_pct  = 1.0  # 1% risk per trade
                        risk_amt  = capital * risk_pct / 100
                        qty       = int(risk_amt / rr_data['risk']) if rr_data['risk'] > 0 else 0
                        profit    = qty * rr_data['reward']
                        self.detail_text.insert(tk.END,
                            f"  ₹{capital:>8,}  →  {qty:>5} units  "
                            f"Risk ₹{risk_amt:>6,.0f}  Profit ₹{profit:>8,.0f}\n", 'value')
                    self.detail_text.insert(tk.END,
                        "  (Based on 1% capital risk per trade)\n\n", 'label')
        except Exception:
            pass  # Don't break detail view if parsing fails

        # ── BULKOWSKI STATISTICS ──
        if db_match:
            self.detail_text.insert(tk.END, "─── BULKOWSKI STATISTICS (2005) ────────\n", 'divider')

            if db_match.get('description'):
                self.detail_text.insert(tk.END, f"{db_match['description']}\n\n", 'label')

            stats = db_match.get('stats', {})
            if 'bull_market' in stats:
                bm = stats['bull_market']
                self.detail_text.insert(tk.END, "BULL MARKET:\n", 'bullish')
                for k, v in bm.items():
                    k_fmt = k.replace('_', ' ').title()
                    self.detail_text.insert(tk.END, f"  {k_fmt:<30} ", 'label')
                    self.detail_text.insert(tk.END, f"{v}\n", 'value')
                self.detail_text.insert(tk.END, "\n")

            if 'bear_market' in stats:
                bm = stats['bear_market']
                self.detail_text.insert(tk.END, "BEAR MARKET:\n", 'bearish')
                for k, v in bm.items():
                    k_fmt = k.replace('_', ' ').title()
                    self.detail_text.insert(tk.END, f"  {k_fmt:<30} ", 'label')
                    self.detail_text.insert(tk.END, f"{v}\n", 'value')
                self.detail_text.insert(tk.END, "\n")

            if db_match.get('measure_rule'):
                self.detail_text.insert(tk.END, "MEASURE RULE (Target Method):\n", 'header')
                self.detail_text.insert(tk.END, f"{db_match['measure_rule']}\n", 'value')
                self.detail_text.insert(tk.END, f"Reliability: {db_match.get('target_reliability', 'N/A')}\n\n", 'label')

            # Detailed trading plan from DB
            tp = db_match.get('trading_plan', {})
            if tp:
                self.detail_text.insert(tk.END, "─── DETAILED TRADING RULES ─────────────\n", 'divider')
                field_map = {
                    'entry': ('▸ ENTRY',  'entry'),
                    'stop':  ('▸ STOP',   'stop'),
                    'target_1': ('▸ TARGET 1', 'target'),
                    'target_2': ('▸ TARGET 2', 'target'),
                    'exit_rule': ('▸ EXIT RULE', 'label'),
                    'avoid':     ('▸ AVOID',     'warning'),
                }
                for field, (label, tag) in field_map.items():
                    if field in tp:
                        self.detail_text.insert(tk.END, f"{label}:\n", tag)
                        self.detail_text.insert(tk.END, f"  {tp[field]}\n\n", 'value')

            # Best performance tips
            best = db_match.get('best_performance', [])
            if best:
                self.detail_text.insert(tk.END, "─── FOR BEST PERFORMANCE ────────────────\n", 'divider')
                for tip in best:
                    self.detail_text.insert(tk.END, f"  ★ {tip}\n", 'best')
                self.detail_text.insert(tk.END, "\n")

            # Identification guidelines
            id_rules = db_match.get('identification', [])
            if id_rules:
                self.detail_text.insert(tk.END, "─── IDENTIFICATION CHECKLIST ────────────\n", 'divider')
                for rule in id_rules:
                    self.detail_text.insert(tk.END, f"  ✓ {rule}\n", 'rule')

        else:
            self.detail_text.insert(tk.END, "─── PATTERN NOT IN CURRENT DATABASE ────\n", 'divider')
            self.detail_text.insert(tk.END, "Click 'Pattern Library' to browse all\n53 patterns from the Bulkowski database.\n", 'label')

        # ── KAKUSHADZE QUANT SIGNALS SUMMARY ──────────────────────────────
        if self.df is not None:
            try:
                q_sigs = compute_quant_signals(self.df)
                score_result = compute_combined_score(q_sigs, pat['direction'])
                if len(score_result) == 6:
                    score, verdict, v_color, agree, disagree, neutral_ct = score_result
                    self.detail_text.insert(tk.END,
                        "\n─── KAKUSHADZE QUANT CONFIRMATION ──────\n", 'divider')
                    self.detail_text.insert(tk.END,
                        f"  Agreement score:  {score}%\n", 'header')
                    v_tag = 'entry' if score >= 75 else ('target' if score >= 50 else ('warning' if score >= 25 else 'stop'))
                    self.detail_text.insert(tk.END,
                        f"  Verdict:          {verdict}\n", v_tag)
                    self.detail_text.insert(tk.END,
                        f"  Signals agree:    {agree} / {len(q_sigs)}\n", 'label')
                    self.detail_text.insert(tk.END,
                        f"  Signals conflict: {disagree} / {len(q_sigs)}\n", 'label')
                    self.detail_text.insert(tk.END,
                        f"  Neutral:          {neutral_ct} / {len(q_sigs)}\n\n", 'label')

                    # Quick summary of each signal
                    for sig in q_sigs:
                        col_tag = 'entry' if sig['color'] == '#2ecc71' else \
                                  ('stop'  if sig['color'] == '#e74c3c' else \
                                  ('target' if sig['color'] in ('#f1c40f','#e67e22') else 'label'))
                        self.detail_text.insert(tk.END,
                            f"  {sig['icon']} {sig['name'][:28]:<28}  {sig['signal']}\n", col_tag)

                    self.detail_text.insert(tk.END,
                        "\n  → Click '📈 Quant Signals' for full details\n", 'rule')
            except Exception:
                pass

        self.detail_text.config(state='disabled')

    def _show_quant_signals(self):
        """Full Kakushadze Quantitative Signal Dashboard window."""
        if self.df is None:
            messagebox.showwarning("No Data", "Please load a CSV file first.")
            return

        win = tk.Toplevel(self.root)
        win.title("📈 Kakushadze Quantitative Signal Dashboard — 18 Signals")
        win.geometry('1000x820')
        win.configure(bg='#f5f5f5')

        # ── HEADER ──
        hdr = tk.Frame(win, bg='#f5f5f5', pady=8, padx=16)
        hdr.pack(fill='x')
        tk.Label(hdr,
                 text="📈  KAKUSHADZE QUANTITATIVE SIGNAL DASHBOARD",
                 bg='#f5f5f5', fg='#f1c40f',
                 font=('Consolas', 13, 'bold')).pack(side='left')
        tk.Label(hdr,
                 text="151 Trading Strategies — Kakushadze & Serur (2018)",
                 bg='#f5f5f5', fg='#777',
                 font=('Consolas', 9)).pack(side='left', padx=16)

        # ── COMPUTE SIGNALS ──
        try:
            q_sigs = compute_quant_signals(self.df)
        except Exception as e:
            messagebox.showerror("Error", f"Could not compute signals:\n{e}")
            win.destroy()
            return

        # ── COMBINED SCORE BAR ──
        # Get direction from top detected pattern if available
        top_dir = self.detected[0]['direction'] if self.detected else 'BULLISH'
        try:
            score, verdict, v_color, agree, disagree, neutral_ct = \
                compute_combined_score(q_sigs, top_dir)
        except Exception:
            score, verdict, v_color, agree, disagree, neutral_ct = 50, 'N/A', '#888', 0, 0, 0

        score_frame = tk.Frame(win, bg='#f0f0f0', pady=10, padx=20)
        score_frame.pack(fill='x', padx=10, pady=4)

        tk.Label(score_frame,
                 text=f"PATTERN DIRECTION: {top_dir}",
                 bg='#f0f0f0', fg='#555555',
                 font=('Consolas', 9)).pack(side='left')

        tk.Label(score_frame,
                 text=f"  QUANT AGREEMENT: {score}%  —  {verdict}",
                 bg='#f0f0f0', fg=v_color,
                 font=('Consolas', 11, 'bold')).pack(side='left', padx=20)

        bar_filled = int(score / 10)
        bar_str    = "█" * bar_filled + "░" * (10 - bar_filled)
        tk.Label(score_frame,
                 text=f"[{bar_str}]",
                 bg='#f0f0f0', fg=v_color,
                 font=('Consolas', 11)).pack(side='left')

        tk.Label(score_frame,
                 text=f"  ✅{agree}  ❌{disagree}  ◆{neutral_ct}",
                 bg='#f0f0f0', fg='#555555',
                 font=('Consolas', 9)).pack(side='left', padx=10)

        # ── SIGNAL CARDS ──
        # Use a canvas with scrollbar for the signal cards
        canvas_frame = tk.Frame(win, bg='#f5f5f5')
        canvas_frame.pack(fill='both', expand=True, padx=10, pady=4)

        vsb = tk.Scrollbar(canvas_frame, orient='vertical')
        vsb.pack(side='right', fill='y')
        hcanvas = tk.Canvas(canvas_frame, bg='#f5f5f5',
                            yscrollcommand=vsb.set, highlightthickness=0)
        hcanvas.pack(side='left', fill='both', expand=True)
        vsb.config(command=hcanvas.yview)

        inner = tk.Frame(hcanvas, bg='#f5f5f5')
        inner_id = hcanvas.create_window((0, 0), window=inner, anchor='nw')

        def on_configure(event):
            hcanvas.configure(scrollregion=hcanvas.bbox('all'))
            hcanvas.itemconfig(inner_id, width=event.width)

        hcanvas.bind('<Configure>', on_configure)

        # ── DETAIL PANEL (right side when signal selected) ──
        main_pane = tk.PanedWindow(win, orient='horizontal',
                                   bg='#f5f5f5', sashwidth=6)
        main_pane.pack(fill='both', expand=True, padx=10, pady=4)

        # Left: signal list
        left_frame = tk.Frame(main_pane, bg='#f5f5f5')
        main_pane.add(left_frame, width=340)

        sig_listbox = tk.Listbox(
            left_frame, bg='#f0f0f0', fg='#1a1d23',
            selectbackground='#1f6feb',
            font=('Consolas', 9), relief='flat',
            activestyle='none', height=20
        )
        sig_scrollbar = tk.Scrollbar(left_frame, command=sig_listbox.yview)
        sig_listbox.config(yscrollcommand=sig_scrollbar.set)
        sig_scrollbar.pack(side='right', fill='y')
        sig_listbox.pack(fill='both', expand=True)

        # Right: detail
        right_frame = tk.Frame(main_pane, bg='#f5f5f5')
        main_pane.add(right_frame)

        detail = scrolledtext.ScrolledText(
            right_frame, bg='#f5f5f5', fg='#1a1d23',
            font=('Consolas', 9), wrap=tk.WORD,
            relief='flat', padx=12, pady=8)
        detail.pack(fill='both', expand=True)
        detail.tag_config('h1',    foreground='#f1c40f', font=('Consolas', 11, 'bold'))
        detail.tag_config('h2',    foreground='#3498db', font=('Consolas', 10, 'bold'))
        detail.tag_config('bull',  foreground='#2ecc71', font=('Consolas', 10, 'bold'))
        detail.tag_config('bear',  foreground='#e74c3c', font=('Consolas', 10, 'bold'))
        detail.tag_config('warn',  foreground='#e67e22', font=('Consolas', 10, 'bold'))
        detail.tag_config('neut',  foreground='#7f8c8d', font=('Consolas', 10, 'bold'))
        detail.tag_config('lbl',   foreground='#555555')
        detail.tag_config('val',   foreground='#1a1d23')
        detail.tag_config('rule',  foreground='#55aabb')
        detail.tag_config('div',   foreground='#333')
        detail.tag_config('src',   foreground='#6d28d9', font=('Consolas', 8))

        # Populate signal list
        for sig in q_sigs:
            bar_len    = int(sig['strength'] / 10)
            bar_filled = "█" * bar_len + "░" * (10 - bar_len)
            sig_listbox.insert(
                tk.END,
                f" {sig['icon']} {sig['name'][:26]:<26}  [{bar_filled}]"
            )

        def on_sig_select(event):
            sel = sig_listbox.curselection()
            if not sel: return
            idx = sel[0]
            sig = q_sigs[idx]

            detail.config(state='normal')
            detail.delete(1.0, tk.END)

            # Signal header
            detail.insert(tk.END, f"\n{sig['name'].upper()}\n", 'h1')
            detail.insert(tk.END, f"Source: {sig['source']}\n", 'src')
            detail.insert(tk.END, "─" * 44 + "\n\n", 'div')

            # Signal value
            sig_tag = 'bull' if sig['color'] == '#2ecc71' else \
                      ('bear' if sig['color'] == '#e74c3c' else \
                      ('warn' if sig['color'] in ('#f39c12','#e67e22') else 'neut'))
            detail.insert(tk.END, f"SIGNAL:   {sig['icon']} {sig['signal']}\n", sig_tag)

            # Strength bar
            s = sig['strength']
            sb = "█" * int(s/10) + "░" * (10 - int(s/10))
            detail.insert(tk.END, f"STRENGTH: {s:.0f}%  [{sb}]\n\n", 'lbl')

            detail.insert(tk.END, f"VALUE:\n  {sig['value']}\n\n", 'val')

            # Description
            detail.insert(tk.END, "─── EXPLANATION ─────────────────────────\n", 'div')
            detail.insert(tk.END, f"{sig['desc']}\n\n", 'val')

            # Trading rules
            detail.insert(tk.END, "─── TRADING RULES ───────────────────────\n", 'div')
            for line in sig['trade_rule'].split('\n'):
                if line.strip().startswith('→'):
                    detail.insert(tk.END, f"{line}\n", 'rule')
                else:
                    detail.insert(tk.END, f"{line}\n", 'val')

            # Agreement with detected patterns
            if self.detected:
                detail.insert(tk.END, "\n─── PATTERN INTERACTION ────────────────\n", 'div')
                for p in self.detected[:3]:
                    pdir = p['direction']
                    is_agree = (
                        ('BULL' in pdir and sig['color'] == '#2ecc71') or
                        ('BEAR' in pdir and sig['color'] == '#e74c3c')
                    )
                    icon = '✅' if is_agree else ('❌' if sig['color'] in ('#2ecc71','#e74c3c') else '◆')
                    detail.insert(tk.END,
                        f"  {icon} {p['name'][:30]}  ({pdir[:8]})\n",
                        'rule' if is_agree else 'warn')

            detail.config(state='disabled')

        sig_listbox.bind('<<ListboxSelect>>', on_sig_select)

        # ── SUMMARY TABLE AT BOTTOM ──
        summary_frame = tk.Frame(win, bg='#f0f0f0', pady=6, padx=16)
        summary_frame.pack(fill='x', padx=10, pady=4)

        tk.Label(summary_frame,
                 text="QUICK SUMMARY:",
                 bg='#f0f0f0', fg='#f1c40f',
                 font=('Consolas', 9, 'bold')).pack(side='left')

        for sig in q_sigs:
            lbl = tk.Label(summary_frame,
                           text=f"  {sig['icon']} {sig['name'].split('(')[0].strip()[:12]}",
                           bg='#f0f0f0', fg=sig['color'],
                           font=('Consolas', 8))
            lbl.pack(side='left')

        # Auto-select first signal
        sig_listbox.selection_set(0)
        on_sig_select(None)

    def _show_brooks(self):
        """Al Brooks Price Action Signal Dashboard."""
        if self.df is None:
            messagebox.showwarning("No Data", "Please load a CSV file first.")
            return

        win = tk.Toplevel(self.root)
        win.title("📐 Al Brooks Price Action Dashboard")
        win.geometry('1020x760')
        win.configure(bg='#f5f5f5')

        # Header
        hdr = tk.Frame(win, bg='#f5f5f5', pady=8, padx=16)
        hdr.pack(fill='x')
        tk.Label(hdr, text="📐  AL BROOKS PRICE ACTION SIGNALS",
                 bg='#f5f5f5', fg='#2c7a4b',
                 font=('Consolas', 13, 'bold')).pack(side='left')
        tk.Label(hdr, text="Trading Price Action Trends — Al Brooks (Wiley, 2012)",
                 bg='#f5f5f5', fg='#777',
                 font=('Consolas', 9)).pack(side='left', padx=16)

        # Compute signals
        try:
            brooks_sigs = detect_brooks_signals(self.df)
        except Exception as e:
            messagebox.showerror("Error", f"Could not compute Brooks signals:\n{e}")
            win.destroy()
            return

        # Summary bar
        summary = tk.Frame(win, bg='#f0f0f0', pady=8, padx=16)
        summary.pack(fill='x', padx=10, pady=4)
        count = len(brooks_sigs)
        tk.Label(summary,
                 text=f"Signals detected: {count}  |  Load more data for richer analysis  |  All computed from OHLC only",
                 bg='#f0f0f0', fg='#555555',
                 font=('Consolas', 9)).pack(side='left')

        # Main pane
        pane = tk.PanedWindow(win, orient='horizontal',
                              bg='#f5f5f5', sashwidth=6)
        pane.pack(fill='both', expand=True, padx=10, pady=4)

        # Left: signal list
        left = tk.Frame(pane, bg='#f5f5f5')
        pane.add(left, width=360)

        # Library section header
        tk.Label(left, text="DETECTED SIGNALS",
                 bg='#f5f5f5', fg='#2c7a4b',
                 font=('Consolas', 10, 'bold'), pady=4).pack(fill='x')

        lb_frame = tk.Frame(left, bg='#f5f5f5')
        lb_frame.pack(fill='both', expand=False)
        lb_sb = tk.Scrollbar(lb_frame, orient='vertical')
        lb = tk.Listbox(lb_frame, bg='#f0f0f0', fg='#1a1d23',
                        selectbackground='#2c7a4b',
                        font=('Consolas', 9), relief='flat',
                        activestyle='none', height=8,
                        yscrollcommand=lb_sb.set)
        lb_sb.config(command=lb.yview)
        lb_sb.pack(side='right', fill='y')
        lb.pack(fill='x')

        # Full library section
        tk.Label(left, text="FULL BROOKS STRATEGY LIBRARY (12)",
                 bg='#f5f5f5', fg='#777',
                 font=('Consolas', 9, 'bold'), pady=4).pack(fill='x')

        lib_frame = tk.Frame(left, bg='#f5f5f5')
        lib_frame.pack(fill='both', expand=True)
        lib_sb = tk.Scrollbar(lib_frame, orient='vertical')
        lib_lb = tk.Listbox(lib_frame, bg='#f5f5f5', fg='#555555',
                            selectbackground='#2c7a4b',
                            font=('Consolas', 8), relief='flat',
                            activestyle='none',
                            yscrollcommand=lib_sb.set)
        lib_sb.config(command=lib_lb.yview)
        lib_sb.pack(side='right', fill='y')
        lib_lb.pack(fill='both', expand=True)

        # Right: detail
        right = tk.Frame(pane, bg='#f5f5f5')
        pane.add(right)
        det = scrolledtext.ScrolledText(
            right, bg='#f5f5f5', fg='#1a1d23',
            font=('Consolas', 9), wrap=tk.WORD,
            relief='flat', padx=12, pady=8)
        det.pack(fill='both', expand=True)
        det.tag_config('h1',   foreground='#2c7a4b', font=('Consolas', 11, 'bold'))
        det.tag_config('h2',   foreground='#f1c40f', font=('Consolas', 10, 'bold'))
        det.tag_config('bull', foreground='#2ecc71', font=('Consolas', 9, 'bold'))
        det.tag_config('bear', foreground='#e74c3c', font=('Consolas', 9, 'bold'))
        det.tag_config('neut', foreground='#f1c40f', font=('Consolas', 9, 'bold'))
        det.tag_config('lbl',  foreground='#555555')
        det.tag_config('val',  foreground='#1a1d23')
        det.tag_config('en',   foreground='#2ecc71', font=('Consolas', 9, 'bold'))
        det.tag_config('st',   foreground='#e74c3c', font=('Consolas', 9, 'bold'))
        det.tag_config('tg',   foreground='#f1c40f', font=('Consolas', 9, 'bold'))
        det.tag_config('mg',   foreground='#9b59b6', font=('Consolas', 9, 'bold'))
        det.tag_config('fp',   foreground='#3498db', font=('Consolas', 8))
        det.tag_config('src',  foreground='#6d28d9', font=('Consolas', 8))
        det.tag_config('div',  foreground='#2a2a2a')
        det.tag_config('rule', foreground='#55aabb', font=('Consolas', 8))
        det.tag_config('edge', foreground='#1a7a4a', font=('Consolas', 9, 'bold'))

        def show_signal(sig_data):
            """Show a detected signal in the detail panel."""
            det.config(state='normal')
            det.delete(1.0, tk.END)
            det.insert(tk.END, f"\n{sig_data['name'].upper()}\n", 'h1')
            det.insert(tk.END, f"Source: {sig_data['source']}\n", 'src')
            det.insert(tk.END, "─" * 46 + "\n\n", 'div')

            sig_tag = 'bull' if '▲' in sig_data['signal'] else ('bear' if '▼' in sig_data['signal'] else 'neut')
            det.insert(tk.END, f"SIGNAL:     {sig_data['signal']}\n", sig_tag)
            conf = sig_data.get('confidence', 0)
            cb = "█" * int(conf/10) + "░" * (10-int(conf/10))
            det.insert(tk.END, f"CONFIDENCE: {conf}%  [{cb}]\n\n", 'lbl')
            det.insert(tk.END, f"VALUE:\n  {sig_data['value']}\n\n", 'val')

            det.insert(tk.END, "─── TRADING PLAN ─────────────────────────────\n", 'div')
            det.insert(tk.END, "▸ ENTRY:\n", 'en')
            det.insert(tk.END, f"  {sig_data['entry']}\n\n", 'val')
            det.insert(tk.END, "▸ STOP:\n", 'st')
            det.insert(tk.END, f"  {sig_data['stop']}\n\n", 'val')
            det.insert(tk.END, "▸ TARGET:\n", 'tg')
            det.insert(tk.END, f"  {sig_data['target']}\n\n", 'val')

            det.insert(tk.END, "─── EXPLANATION ──────────────────────────────\n", 'div')
            det.insert(tk.END, f"{sig_data['desc']}\n", 'val')
            det.config(state='disabled')

        def show_library_entry(name):
            """Show a Brooks library entry in the detail panel."""
            db = BROOKS_DB.get(name)
            if not db:
                return
            det.config(state='normal')
            det.delete(1.0, tk.END)
            det.insert(tk.END, f"\n{name.upper()}\n", 'h1')
            det.insert(tk.END, f"Source: {db['source']}\n", 'src')
            det.insert(tk.END, f"Type: {db['type'].upper()}  |  Direction: {db['direction'].upper()}\n\n", 'lbl')

            det.insert(tk.END, "─── FIRST PRINCIPLE ──────────────────────────\n", 'div')
            det.insert(tk.END, f"{db['first_principle']}\n\n", 'fp')

            det.insert(tk.END, "─── IDENTIFICATION CHECKLIST ─────────────────\n", 'div')
            for item in db['identification']:
                det.insert(tk.END, f"  ✓ {item}\n", 'rule')
            det.insert(tk.END, "\n")

            det.insert(tk.END, "─── TRADING PLAN ─────────────────────────────\n", 'div')
            tp = db['trading_plan']
            for field, label, tag in [
                ('entry',    '▸ ENTRY',    'en'),
                ('stop',     '▸ STOP',     'st'),
                ('target_1', '▸ TARGET 1', 'tg'),
                ('target_2', '▸ TARGET 2', 'tg'),
                ('target_3', '▸ TARGET 3', 'tg'),
                ('manage',   '▸ MANAGE',   'mg'),
                ('avoid',    '▸ AVOID',    'bear'),
            ]:
                if field in tp:
                    det.insert(tk.END, f"{label}:\n", tag)
                    det.insert(tk.END, f"  {tp[field]}\n\n", 'val')

            det.insert(tk.END, "─── CONVERGENCE EDGE ─────────────────────────\n", 'div')
            det.insert(tk.END, f"{db['edge']}\n", 'edge')
            det.config(state='disabled')

        # Populate detected signals list
        if brooks_sigs:
            for sig in brooks_sigs:
                sig_icon = sig.get('icon', '◆')
                lb.insert(tk.END, f" {sig_icon} {sig['name'][8:][:30]:<30}  {sig['confidence']}%")
        else:
            lb.insert(tk.END, "  No Brooks signals detected")
            lb.insert(tk.END, "  (need 10+ bars, clear bar patterns)")

        # Populate full library list
        for name in BROOKS_DB:
            db = BROOKS_DB[name]
            d_icon = "▲" if db['direction'] == 'bullish' else ("▼" if db['direction'] == 'bearish' else "◆")
            lib_lb.insert(tk.END, f" {d_icon} {name}")

        def on_signal_select(event):
            sel = lb.curselection()
            if not sel or not brooks_sigs: return
            show_signal(brooks_sigs[sel[0]])

        def on_library_select(event):
            sel = lib_lb.curselection()
            if not sel: return
            name = lib_lb.get(sel[0]).strip()[2:]  # remove icon prefix
            show_library_entry(name)

        lb.bind('<<ListboxSelect>>', on_signal_select)
        lib_lb.bind('<<ListboxSelect>>', on_library_select)

        # Auto-select first detected signal or first library entry
        if brooks_sigs:
            lb.selection_set(0)
            show_signal(brooks_sigs[0])
        else:
            lib_lb.selection_set(0)
            first_name = list(BROOKS_DB.keys())[0]
            show_library_entry(first_name)

        # Bottom info bar
        info = tk.Frame(win, bg='#f0f0f0', pady=5, padx=16)
        info.pack(fill='x', padx=10, pady=4)
        tk.Label(info,
                 text="💡 Top panel = auto-detected signals from your chart  |  Bottom panel = full library: click any strategy to read its plan",
                 bg='#f0f0f0', fg='#555555',
                 font=('Consolas', 8)).pack(side='left')

    def _show_street_smarts_inline(self, sig):
        """Show a Street Smarts signal in the main detail panel."""
        SS_COL = '#cd853f'
        self.detail_text.config(state='normal')
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.insert(tk.END, f"\n{sig['name'].upper()}\n", 'header')
        self.detail_text.insert(tk.END, f"Source: {sig['source']}\n", 'rule')
        self.detail_text.insert(tk.END, "─" * 40 + "\n\n", 'divider')
        s_tag = 'bullish' if '▲' in sig['signal'] else ('bearish' if '▼' in sig['signal'] else 'neutral')
        conf = sig.get('confidence', 0)
        cb   = "█" * int(conf/10) + "░" * (10 - int(conf/10))
        self.detail_text.insert(tk.END, f"SIGNAL:     {sig['signal']}\n", s_tag)
        self.detail_text.insert(tk.END, f"CONFIDENCE: {conf}%  [{cb}]\n\n", 'label')
        self.detail_text.insert(tk.END, f"VALUE:\n  {sig['value']}\n\n", 'value')

        self.detail_text.insert(tk.END, "─── TRADING PLAN ────────────────────────\n", 'divider')
        self.detail_text.insert(tk.END, "▸ ENTRY:\n",  'entry')
        self.detail_text.insert(tk.END, f"  {sig['entry']}\n\n", 'value')
        self.detail_text.insert(tk.END, "▸ STOP:\n",   'stop')
        self.detail_text.insert(tk.END, f"  {sig['stop']}\n\n",  'value')
        self.detail_text.insert(tk.END, "▸ TARGET:\n", 'target')
        self.detail_text.insert(tk.END, f"  {sig['target']}\n\n", 'value')

        # R:R auto-calculation
        try:
            import re as _re
            def ep(s):
                nums = _re.findall(r'\d+\.?\d*', str(s))
                return float(nums[0]) if nums else None
            ev = ep(sig['entry']); sv = ep(sig['stop']); tv = ep(sig['target'])
            if ev and sv and tv:
                rr = calc_rr(ev, sv, tv)
                if rr:
                    self.detail_text.insert(tk.END,
                        "─── R:R CALCULATOR ──────────────────────\n", 'divider')
                    self.detail_text.insert(tk.END,
                        f"  Risk:  {rr['risk']:.2f}  |  Reward: {rr['reward']:.2f}\n", 'label')
                    rr_tag = 'entry' if rr['rr'] >= 2 else ('warning' if rr['rr'] >= 1 else 'stop')
                    self.detail_text.insert(tk.END,
                        f"  R:R:   1 : {rr['rr']:.1f}  Grade: {rr['grade']}\n", rr_tag)
                    self.detail_text.insert(tk.END,
                        f"  {rr['advice']}\n\n", 'value')
        except Exception:
            pass

        self.detail_text.insert(tk.END,
            "─── EXPLANATION ─────────────────────────\n", 'divider')
        self.detail_text.insert(tk.END, f"{sig['desc']}\n\n", 'value')

        # Lookup in STREET_SMARTS_DB for extra detail
        name_clean = sig['name'].replace('Street Smarts: ', '').split('(')[0].strip()
        for key in STREET_SMARTS_DB:
            if any(w.lower() in key.lower() for w in name_clean.split()[:2]):
                db = STREET_SMARTS_DB[key]
                self.detail_text.insert(tk.END,
                    "─── 2025 REVIEW ─────────────────────────\n", 'divider')
                self.detail_text.insert(tk.END,
                    f"  {db['rating']}\n", 'best')
                self.detail_text.insert(tk.END,
                    f"  {db['review_2025']}\n\n", 'rule')
                if db.get('pre_market'):
                    self.detail_text.insert(tk.END,
                        "─── PRE-MARKET CONDITIONS ───────────────\n", 'divider')
                    for item in db['pre_market']:
                        self.detail_text.insert(tk.END, f"  ◆ {item}\n", 'rule')
                break
        self.detail_text.config(state='disabled')

    def _show_street_smarts(self):
        """Full Street Smarts Dashboard window."""
        if self.df is None:
            messagebox.showwarning("No Data", "Please load a CSV file first.")
            return

        win = tk.Toplevel(self.root)
        win.title("🎯 Street Smarts — Raschke & Connors Dashboard")
        win.geometry('1040x780')
        win.configure(bg='#f5f5f5')

        SS_COL = '#cd853f'

        # Header
        hdr = tk.Frame(win, bg='#f5f5f5', pady=8, padx=16)
        hdr.pack(fill='x')
        tk.Label(hdr,
                 text="🎯  STREET SMARTS — RASCHKE & CONNORS (1996)",
                 bg='#f5f5f5', fg=SS_COL,
                 font=('Consolas', 13, 'bold')).pack(side='left')
        tk.Label(hdr,
                 text="High Probability Short-Term Trading Strategies",
                 bg='#f5f5f5', fg='#777',
                 font=('Consolas', 9)).pack(side='left', padx=16)

        # Compute signals
        try:
            ss_sigs = detect_street_smarts(self.df)
            self.street_smarts = ss_sigs
        except Exception as e:
            messagebox.showerror("Error", f"Could not compute signals:\n{e}")
            win.destroy()
            return

        # Summary bar
        summary = tk.Frame(win, bg='#fff8e8', pady=8, padx=16)
        summary.pack(fill='x', padx=10, pady=4)
        tk.Label(summary,
                 text=f"Auto-detected: {len(ss_sigs)} signals   |   "
                      f"Library: {len(STREET_SMARTS_DB)} strategies   |   "
                      f"All computed from OHLC data only",
                 bg='#fff8e8', fg='#cd853f',
                 font=('Consolas', 9)).pack(side='left')

        # Main pane
        pane = tk.PanedWindow(win, orient='horizontal',
                              bg='#f5f5f5', sashwidth=6)
        pane.pack(fill='both', expand=True, padx=10, pady=4)

        # Left panel
        left = tk.Frame(pane, bg='#f5f5f5')
        pane.add(left, width=360)

        tk.Label(left, text="DETECTED SIGNALS",
                 bg='#f5f5f5', fg=SS_COL,
                 font=('Consolas', 10, 'bold'), pady=4).pack(fill='x')

        lb_frame = tk.Frame(left, bg='#f5f5f5')
        lb_frame.pack(fill='x')
        lb_sb = tk.Scrollbar(lb_frame, orient='vertical')
        lb = tk.Listbox(lb_frame, bg='#fff5e0', fg='#1a1d23',
                        selectbackground='#8B4513',
                        font=('Consolas', 9), relief='flat',
                        activestyle='none', height=8,
                        yscrollcommand=lb_sb.set)
        lb_sb.config(command=lb.yview)
        lb_sb.pack(side='right', fill='y')
        lb.pack(fill='x')

        tk.Label(left, text="FULL STRATEGY LIBRARY (12)",
                 bg='#f5f5f5', fg='#777',
                 font=('Consolas', 9, 'bold'), pady=4).pack(fill='x')

        lib_fr = tk.Frame(left, bg='#f5f5f5')
        lib_fr.pack(fill='both', expand=True)
        lib_sb = tk.Scrollbar(lib_fr, orient='vertical')
        lib_lb = tk.Listbox(lib_fr, bg='#f5f5f5', fg='#555555',
                            selectbackground='#8B4513',
                            font=('Consolas', 8), relief='flat',
                            activestyle='none',
                            yscrollcommand=lib_sb.set)
        lib_sb.config(command=lib_lb.yview)
        lib_sb.pack(side='right', fill='y')
        lib_lb.pack(fill='both', expand=True)

        # Right panel
        right = tk.Frame(pane, bg='#f5f5f5')
        pane.add(right)
        det = scrolledtext.ScrolledText(
            right, bg='#f5f5f5', fg='#1a1d23',
            font=('Consolas', 9), wrap=tk.WORD,
            relief='flat', padx=12, pady=8)
        det.pack(fill='both', expand=True)
        det.tag_config('h1',   foreground=SS_COL,    font=('Consolas', 11, 'bold'))
        det.tag_config('src',  foreground='#6d28d9', font=('Consolas', 8))
        det.tag_config('bull', foreground='#2ecc71', font=('Consolas', 9, 'bold'))
        det.tag_config('bear', foreground='#e74c3c', font=('Consolas', 9, 'bold'))
        det.tag_config('neut', foreground='#f1c40f', font=('Consolas', 9, 'bold'))
        det.tag_config('lbl',  foreground='#555555')
        det.tag_config('val',  foreground='#1a1d23')
        det.tag_config('en',   foreground='#2ecc71', font=('Consolas', 9, 'bold'))
        det.tag_config('st',   foreground='#e74c3c', font=('Consolas', 9, 'bold'))
        det.tag_config('tg',   foreground='#f1c40f', font=('Consolas', 9, 'bold'))
        det.tag_config('mg',   foreground='#9b59b6', font=('Consolas', 9))
        det.tag_config('fp',   foreground='#3498db', font=('Consolas', 8))
        det.tag_config('div',  foreground='#2a2a2a')
        det.tag_config('rule', foreground='#cd853f', font=('Consolas', 8))
        det.tag_config('rev',  foreground='#27ae60', font=('Consolas', 8, 'bold'))
        det.tag_config('warn', foreground='#e74c3c', font=('Consolas', 8))
        det.tag_config('rate', foreground=SS_COL,    font=('Consolas', 9, 'bold'))

        def show_detected(sig):
            det.config(state='normal')
            det.delete(1.0, tk.END)
            det.insert(tk.END, f"\n{sig['name'].upper()}\n", 'h1')
            det.insert(tk.END, f"Source: {sig['source']}\n", 'src')
            det.insert(tk.END, "─" * 46 + "\n\n", 'div')
            s_tag = 'bull' if '▲' in sig['signal'] else ('bear' if '▼' in sig['signal'] else 'neut')
            det.insert(tk.END, f"SIGNAL:     {sig['signal']}\n", s_tag)
            conf = sig.get('confidence', 0)
            det.insert(tk.END, f"CONFIDENCE: {conf}%  [{'█'*int(conf/10)}{'░'*(10-int(conf/10))}]\n\n", 'lbl')
            det.insert(tk.END, f"VALUE:\n  {sig['value']}\n\n", 'val')
            det.insert(tk.END, "─── TRADING PLAN ──────────────────────────\n", 'div')
            det.insert(tk.END, "▸ ENTRY:\n", 'en')
            det.insert(tk.END, f"  {sig['entry']}\n\n", 'val')
            det.insert(tk.END, "▸ STOP:\n", 'st')
            det.insert(tk.END, f"  {sig['stop']}\n\n", 'val')
            det.insert(tk.END, "▸ TARGET:\n", 'tg')
            det.insert(tk.END, f"  {sig['target']}\n\n", 'val')
            try:
                import re as _re
                def ep(s):
                    nums = _re.findall(r'\d+\.?\d*', str(s))
                    return float(nums[0]) if nums else None
                ev=ep(sig['entry']); sv=ep(sig['stop']); tv=ep(sig['target'])
                if ev and sv and tv:
                    rr = calc_rr(ev, sv, tv)
                    if rr:
                        det.insert(tk.END, "─── R:R ───────────────────────────────────\n", 'div')
                        rr_tag = 'bull' if rr['rr'] >= 2 else ('neut' if rr['rr'] >= 1 else 'bear')
                        det.insert(tk.END, f"  Risk: {rr['risk']:.2f}  Reward: {rr['reward']:.2f}  R:R: 1:{rr['rr']:.1f}  Grade: {rr['grade']}\n", rr_tag)
                        det.insert(tk.END, f"  {rr['advice']}\n\n", 'val')
            except Exception:
                pass
            det.insert(tk.END, "─── EXPLANATION ────────────────────────────\n", 'div')
            det.insert(tk.END, f"{sig['desc']}\n", 'val')
            # 2025 review
            name_c = sig['name'].replace('Street Smarts: ', '').split('(')[0].strip()
            for key in STREET_SMARTS_DB:
                if any(w.lower() in key.lower() for w in name_c.split()[:2]):
                    db = STREET_SMARTS_DB[key]
                    det.insert(tk.END, "\n─── 2025 REVIEW ────────────────────────────\n", 'div')
                    det.insert(tk.END, f"  {db['rating']}\n", 'rate')
                    det.insert(tk.END, f"  {db['review_2025']}\n", 'rev')
                    break
            det.config(state='disabled')

        def show_library(name):
            db = STREET_SMARTS_DB.get(name)
            if not db:
                return
            det.config(state='normal')
            det.delete(1.0, tk.END)
            det.insert(tk.END, f"\n{name.upper()}\n", 'h1')
            det.insert(tk.END, f"Source: {db['source']}\n", 'src')
            det.insert(tk.END, f"Type: {db['type'].upper()}  |  {db['rating']}\n\n", 'rate')
            det.insert(tk.END, "─── CONCEPT ───────────────────────────────\n", 'div')
            det.insert(tk.END, f"{db['concept']}\n\n", 'fp')
            if db.get('pre_market'):
                det.insert(tk.END, "─── PRE-MARKET CONDITIONS ─────────────────\n", 'div')
                for item in db['pre_market']:
                    det.insert(tk.END, f"  ◆ {item}\n", 'rule')
                det.insert(tk.END, "\n")
            tp = db['trading_plan']
            det.insert(tk.END, "─── TRADING PLAN ──────────────────────────\n", 'div')
            for field, label, tag in [
                ('entry',    '▸ ENTRY',    'en'),
                ('stop',     '▸ STOP',     'st'),
                ('target_1', '▸ TARGET 1', 'tg'),
                ('target_2', '▸ TARGET 2', 'tg'),
                ('manage',   '▸ MANAGE',   'mg'),
                ('avoid',    '▸ AVOID',    'warn'),
            ]:
                if field in tp:
                    det.insert(tk.END, f"{label}:\n", tag)
                    det.insert(tk.END, f"  {tp[field]}\n\n", 'val')
            det.insert(tk.END, "─── 2025 REVIEW ────────────────────────────\n", 'div')
            det.insert(tk.END, f"{db['review_2025']}\n", 'rev')
            det.config(state='disabled')

        # Populate lists
        for sig in ss_sigs:
            lb.insert(tk.END, f" {sig['icon']} {sig['name'][15:][:32]:<32}  {sig['confidence']}%")
        if not ss_sigs:
            lb.insert(tk.END, "  No signals detected (need 22+ bars)")

        for name in STREET_SMARTS_DB:
            t_icon = '▲' if STREET_SMARTS_DB[name]['direction'] in ('reversal','mean_reversion','with-trend') else '◆'
            lib_lb.insert(tk.END, f" ◆ {name}")

        def on_det_sel(event):
            sel = lb.curselection()
            if sel and ss_sigs and sel[0] < len(ss_sigs):
                show_detected(ss_sigs[sel[0]])

        def on_lib_sel(event):
            sel = lib_lb.curselection()
            if not sel: return
            raw = lib_lb.get(sel[0]).strip()[2:]
            show_library(raw)

        lb.bind('<<ListboxSelect>>', on_det_sel)
        lib_lb.bind('<<ListboxSelect>>', on_lib_sel)

        if ss_sigs:
            lb.selection_set(0)
            show_detected(ss_sigs[0])
        else:
            lib_lb.selection_set(0)
            show_library(list(STREET_SMARTS_DB.keys())[0])

        # Bottom info
        info = tk.Frame(win, bg='#fff5e0', pady=5, padx=16)
        info.pack(fill='x', padx=10, pady=4)
        tk.Label(info,
                 text="💡 Top = auto-detected from your chart  |  Bottom = full library: click any strategy for complete trading plan + 2025 review",
                 bg='#fff5e0', fg='#555555',
                 font=('Consolas', 8)).pack(side='left')

    def _show_rr_calculator(self):
        """Standalone Risk:Reward Calculator window."""
        win = tk.Toplevel(self.root)
        win.title("⚖️ Risk : Reward Calculator")
        win.geometry('480x620')
        win.configure(bg='#f5f5f5')
        win.resizable(False, False)

        tk.Label(win, text="⚖️  RISK : REWARD CALCULATOR",
                 bg='#f5f5f5', fg='#f1c40f',
                 font=('Consolas', 12, 'bold'),
                 pady=10).pack(fill='x')
        tk.Label(win, text="Manual entry — or auto-filled from detected pattern",
                 bg='#f5f5f5', fg='#777',
                 font=('Consolas', 9)).pack()

        form = tk.Frame(win, bg='#f5f5f5', pady=10)
        form.pack(fill='x', padx=24)

        fields = {}
        labels = [
            ('entry_price',  'Entry Price',     '#2ecc71'),
            ('stop_price',   'Stop Loss Price', '#e74c3c'),
            ('target_price', 'Target Price',    '#f1c40f'),
            ('capital',      'Your Capital (₹)','#3498db'),
            ('risk_pct',     'Risk per Trade (%)', '#9b59b6'),
        ]
        defaults = {
            'capital': '100000',
            'risk_pct': '1',
        }
        # Auto-fill from current selected pattern
        if self.detected:
            import re
            def ep(s):
                nums = re.findall(r'\d+\.?\d*', str(s))
                return nums[0] if nums else ''
            sel = self.pattern_listbox.curselection()
            idx = sel[0] if sel else 0
            if idx < len(self.detected):
                p = self.detected[idx]
                defaults['entry_price']  = ep(p['entry'])
                defaults['stop_price']   = ep(p['stop'])
                defaults['target_price'] = ep(p['target'])

        for field, label, color in labels:
            row = tk.Frame(form, bg='#f5f5f5')
            row.pack(fill='x', pady=5)
            tk.Label(row, text=f"{label}:", bg='#f5f5f5', fg=color,
                     font=('Consolas', 10), width=22, anchor='w').pack(side='left')
            var = tk.StringVar(value=defaults.get(field, ''))
            e = tk.Entry(row, textvariable=var, bg='#f0f0f0', fg='#1a1d23',
                         font=('Consolas', 11), relief='solid', bd=1,
                         insertbackground='#1a1d23', width=18)
            e.pack(side='left', padx=6)
            fields[field] = var

        # Result area
        result_frame = tk.Frame(win, bg='#f0f0f0', relief='flat')
        result_frame.pack(fill='both', expand=True, padx=16, pady=8)
        result_text = scrolledtext.ScrolledText(
            result_frame, bg='#f5f5f5', fg='#1a1d23',
            font=('Consolas', 10), wrap=tk.WORD,
            relief='flat', padx=10, pady=8, height=14)
        result_text.pack(fill='both', expand=True)
        result_text.tag_config('h',    foreground='#f1c40f', font=('Consolas', 11, 'bold'))
        result_text.tag_config('g',    foreground='#2ecc71', font=('Consolas', 10, 'bold'))
        result_text.tag_config('r',    foreground='#e74c3c', font=('Consolas', 10, 'bold'))
        result_text.tag_config('y',    foreground='#f1c40f', font=('Consolas', 10, 'bold'))
        result_text.tag_config('b',    foreground='#3498db')
        result_text.tag_config('lbl',  foreground='#555555')
        result_text.tag_config('val',  foreground='#1a1d23')
        result_text.tag_config('warn', foreground='#e67e22', font=('Consolas', 10, 'bold'))
        result_text.tag_config('div',  foreground='#333')

        def calculate():
            result_text.config(state='normal')
            result_text.delete(1.0, tk.END)
            try:
                entry   = float(fields['entry_price'].get())
                stop    = float(fields['stop_price'].get())
                target  = float(fields['target_price'].get())
                capital = float(fields['capital'].get() or 100000)
                rp      = float(fields['risk_pct'].get() or 1) / 100

                rr = calc_rr(entry, stop, target)
                if not rr:
                    result_text.insert(tk.END, "Entry and Stop cannot be the same.", 'r')
                    result_text.config(state='disabled')
                    return

                risk_amt  = capital * rp
                qty       = int(risk_amt / rr['risk']) if rr['risk'] > 0 else 0
                profit    = qty * rr['reward']
                invest    = qty * entry
                stop_loss_total  = qty * rr['risk']
                target_total     = qty * rr['reward']

                result_text.insert(tk.END, "\n  RISK : REWARD ANALYSIS\n", 'h')
                result_text.insert(tk.END, "  " + "─" * 34 + "\n", 'div')
                result_text.insert(tk.END, f"  Risk per unit   ₹{rr['risk']:>10.2f}\n", 'lbl')
                result_text.insert(tk.END, f"  Reward per unit ₹{rr['reward']:>10.2f}\n", 'lbl')

                rr_val = rr['rr']
                rr_tag = 'g' if rr_val >= 2 else ('y' if rr_val >= 1 else 'r')
                result_text.insert(tk.END,
                    f"\n  R:R Ratio  →  1 : {rr_val:.2f}\n", rr_tag)
                grade_tag = 'g' if rr['grade'].startswith('A') else \
                            ('y' if rr['grade'].startswith('B') else \
                            ('warn' if rr['grade'].startswith('C') else 'r'))
                result_text.insert(tk.END,
                    f"  Grade      →  {rr['grade']}\n\n", grade_tag)
                result_text.insert(tk.END,
                    f"  {rr['advice']}\n\n", 'val')

                result_text.insert(tk.END, "  " + "─" * 34 + "\n", 'div')
                result_text.insert(tk.END, "  POSITION SIZING\n", 'h')
                result_text.insert(tk.END, f"  Capital         ₹{capital:>10,.0f}\n", 'lbl')
                result_text.insert(tk.END, f"  Risk budget     ₹{risk_amt:>10,.0f}  ({rp*100:.1f}%)\n", 'lbl')
                result_text.insert(tk.END, f"  Units to buy    {qty:>12,}\n", 'g')
                result_text.insert(tk.END, f"  Investment      ₹{invest:>10,.0f}\n", 'lbl')
                result_text.insert(tk.END, f"\n  Max Loss        ₹{stop_loss_total:>10,.0f}\n", 'r')
                result_text.insert(tk.END, f"  Expected Profit ₹{profit:>10,.0f}\n", 'g')

                # Stop loss levels
                stop_pct = abs(entry - stop) / entry * 100
                tgt_pct  = abs(target - entry) / entry * 100
                result_text.insert(tk.END, "\n  " + "─" * 34 + "\n", 'div')
                result_text.insert(tk.END, f"  Entry  {entry:>10.2f}\n", 'val')
                result_text.insert(tk.END, f"  Stop   {stop:>10.2f}  ({stop_pct:.1f}% away)\n", 'r')
                result_text.insert(tk.END, f"  Target {target:>10.2f}  ({tgt_pct:.1f}% away)\n", 'g')

                # Breakeven
                be_trades = int(1 / (rr_val / (1 + rr_val)) * 10) / 10
                result_text.insert(tk.END,
                    f"\n  Win rate needed to break even: "
                    f"{100/(1+rr_val):.0f}%\n", 'b')

            except ValueError:
                result_text.insert(tk.END,
                    "  ⚠ Please fill in all price fields with numbers.", 'warn')
            result_text.config(state='disabled')

        btn_row = tk.Frame(win, bg='#f5f5f5')
        btn_row.pack(pady=8)
        self._btn(btn_row, "⚖️  CALCULATE", calculate, '#c0392b').pack(side='left', padx=8)
        self._btn(btn_row, "✖  Close",
                  win.destroy, '#333').pack(side='left', padx=8)

        # Auto-calculate if values are pre-filled
        if defaults.get('entry_price'):
            calculate()

    def _show_library(self):
        """Show full pattern library window."""
        lib_win = tk.Toplevel(self.root)
        lib_win.title("Bulkowski Pattern Library — All 53 Patterns")
        lib_win.geometry('900x700')
        lib_win.configure(bg='#f5f5f5')

        tk.Label(lib_win, text="📚 BULKOWSKI PATTERN LIBRARY — Encyclopedia of Chart Patterns (2005)",
                 bg='#f5f5f5', fg='#f1c40f',
                 font=('Consolas', 11, 'bold'), pady=8).pack(fill='x')

        # Search
        search_frame = tk.Frame(lib_win, bg='#f5f5f5')
        search_frame.pack(fill='x', padx=10, pady=4)
        tk.Label(search_frame, text="Search:", bg='#f5f5f5', fg='#777',
                 font=('Consolas', 9)).pack(side='left')
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var,
                                bg='#f0f0f0', fg='white', font=('Consolas', 9),
                                relief='flat', width=30)
        search_entry.pack(side='left', padx=8)

        # Filter by type
        filter_var = tk.StringVar(value="All")
        for label, val in [("All", "All"), ("Bullish", "bullish"), ("Bearish", "bearish"), ("Continuation", "continuation")]:
            rb = tk.Radiobutton(search_frame, text=label, variable=filter_var, value=val,
                                bg='#f5f5f5', fg='#777', selectcolor='#1a1a2e',
                                font=('Consolas', 9))
            rb.pack(side='left', padx=4)

        # Paned window
        pane = tk.PanedWindow(lib_win, orient='horizontal', bg='#f5f5f5', sashwidth=6)
        pane.pack(fill='both', expand=True, padx=10, pady=4)

        # Left: pattern list
        left = tk.Frame(pane, bg='#f5f5f5')
        pane.add(left, width=320)
        lb = tk.Listbox(left, bg='#f0f0f0', fg='#1a1d23',
                        selectbackground='#1f6feb',
                        font=('Consolas', 9), relief='flat')
        sb = tk.Scrollbar(left, command=lb.yview)
        lb.config(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        lb.pack(fill='both', expand=True)

        # Right: detail
        right = tk.Frame(pane, bg='#f5f5f5')
        pane.add(right)
        detail = scrolledtext.ScrolledText(right, bg='#f5f5f5', fg='#1a1d23',
                                           font=('Consolas', 9), wrap=tk.WORD,
                                           relief='flat', padx=8, pady=6)
        detail.pack(fill='both', expand=True)
        detail.tag_config('header',  foreground='#f1c40f', font=('Consolas', 10, 'bold'))
        detail.tag_config('bullish', foreground='#2ecc71', font=('Consolas', 9, 'bold'))
        detail.tag_config('bearish', foreground='#e74c3c', font=('Consolas', 9, 'bold'))
        detail.tag_config('label',   foreground='#555555')
        detail.tag_config('value',   foreground='#1a1d23')
        detail.tag_config('entry',   foreground='#2ecc71', font=('Consolas', 9, 'bold'))
        detail.tag_config('stop',    foreground='#e74c3c', font=('Consolas', 9, 'bold'))
        detail.tag_config('target',  foreground='#f1c40f', font=('Consolas', 9, 'bold'))
        detail.tag_config('warning', foreground='#e67e22')
        detail.tag_config('best',    foreground='#9b59b6')
        detail.tag_config('rule',    foreground='#55aabb')
        detail.tag_config('divider', foreground='#333')

        all_patterns = list(PATTERNS_DB.keys())

        def refresh_list(*args):
            lb.delete(0, tk.END)
            q = search_var.get().lower()
            f = filter_var.get()
            for name in all_patterns:
                db = PATTERNS_DB[name]
                if q and q not in name.lower(): continue
                if f == 'bullish' and db['direction'] != 'bullish': continue
                if f == 'bearish' and db['direction'] != 'bearish': continue
                if f == 'continuation' and db['type'] != 'continuation': continue
                dir_icon = "▲" if db['direction'] == 'bullish' else ("▼" if db['direction'] == 'bearish' else "◆")
                lb.insert(tk.END, f" {dir_icon} {name}")

        def on_select(event):
            sel = lb.curselection()
            if not sel: return
            raw = lb.get(sel[0]).strip()
            # Remove icon
            name = raw[2:].strip()
            if name not in PATTERNS_DB: return
            db = PATTERNS_DB[name]
            detail.config(state='normal')
            detail.delete(1.0, tk.END)
            detail.insert(tk.END, f"\n{name.upper()}\n", 'header')
            detail.insert(tk.END, "─" * 40 + "\n", 'divider')
            dir_tag = 'bullish' if db['direction'] == 'bullish' else 'bearish'
            detail.insert(tk.END, f"Type: {db['type'].upper()} | Direction: {db['direction'].upper()}\n\n", dir_tag)
            detail.insert(tk.END, f"{db.get('description', '')}\n\n", 'label')

            stats = db.get('stats', {})
            if 'bull_market' in stats:
                bm = stats['bull_market']
                detail.insert(tk.END, "BULL MARKET STATISTICS:\n", 'bullish')
                for k, v in bm.items():
                    detail.insert(tk.END, f"  {k.replace('_',' ').title():<28} {v}\n", 'value')
                detail.insert(tk.END, "\n")

            if 'bear_market' in stats:
                bm = stats['bear_market']
                detail.insert(tk.END, "BEAR MARKET STATISTICS:\n", 'bearish')
                for k, v in bm.items():
                    detail.insert(tk.END, f"  {k.replace('_',' ').title():<28} {v}\n", 'value')
                detail.insert(tk.END, "\n")

            if db.get('measure_rule'):
                detail.insert(tk.END, "MEASURE RULE:\n", 'header')
                detail.insert(tk.END, f"{db['measure_rule']}\n", 'value')
                detail.insert(tk.END, f"Reliability: {db.get('target_reliability','N/A')}\n\n", 'label')

            tp = db.get('trading_plan', {})
            if tp:
                detail.insert(tk.END, "TRADING PLAN:\n", 'header')
                for field, label, tag in [
                    ('entry', '▸ ENTRY', 'entry'),
                    ('stop', '▸ STOP', 'stop'),
                    ('target_1', '▸ TARGET 1', 'target'),
                    ('target_2', '▸ TARGET 2', 'target'),
                    ('exit_rule', '▸ EXIT RULE', 'label'),
                    ('avoid', '▸ AVOID', 'warning'),
                ]:
                    if field in tp:
                        detail.insert(tk.END, f"{label}:\n", tag)
                        detail.insert(tk.END, f"  {tp[field]}\n\n", 'value')

            best = db.get('best_performance', [])
            if best:
                detail.insert(tk.END, "BEST PERFORMANCE TIPS:\n", 'header')
                for tip in best:
                    detail.insert(tk.END, f"  ★ {tip}\n", 'best')

            ids = db.get('identification', [])
            if ids:
                detail.insert(tk.END, "\nIDENTIFICATION CHECKLIST:\n", 'header')
                for r in ids:
                    detail.insert(tk.END, f"  ✓ {r}\n", 'rule')
            detail.config(state='disabled')

        search_var.trace('w', refresh_list)
        filter_var.trace('w', refresh_list)
        lb.bind('<<ListboxSelect>>', on_select)
        refresh_list()

    # ─────────────────────────────────────────────────────────────────────────
    #  ANGEL ONE SMARTAPI INTEGRATION
    # ─────────────────────────────────────────────────────────────────────────

    # Pre-loaded instrument token map — covers major indices and top stocks
    # token = (exchange, token_id)
    ANGEL_TOKENS = {
        # ── Indices — use NSE exchange ────────────────────────────────────
        'NIFTY 50':         ('NSE', '99926000'),
        'NIFTY':            ('NSE', '99926000'),
        'BANKNIFTY':        ('NSE', '99926009'),
        'BANK NIFTY':       ('NSE', '99926009'),
        'SENSEX':           ('BSE', '99919000'),
        'NIFTY IT':         ('NSE', '99926024'),
        'NIFTY MIDCAP':     ('NSE', '99926012'),
        'NIFTY FMCG':       ('NSE', '99926035'),
        'NIFTY PHARMA':     ('NSE', '99926045'),
        'NIFTY AUTO':       ('NSE', '99926029'),
        'NIFTY METAL':      ('NSE', '99926037'),
        'NIFTY REALTY':     ('NSE', '99926053'),
        'INDIA VIX':        ('NSE', '99926017'),
        # ── Large cap stocks — NSE EQ ─────────────────────────────────────
        'RELIANCE':         ('NSE', '2885'),
        'RELIANCE-EQ':      ('NSE', '2885'),
        'TCS':              ('NSE', '11536'),
        'TCS-EQ':           ('NSE', '11536'),
        'HDFCBANK':         ('NSE', '1333'),
        'HDFCBANK-EQ':      ('NSE', '1333'),
        'HDFC BANK':        ('NSE', '1333'),
        'INFY':             ('NSE', '1594'),
        'INFY-EQ':          ('NSE', '1594'),
        'INFOSYS':          ('NSE', '1594'),
        'ICICIBANK':        ('NSE', '4963'),
        'ICICIBANK-EQ':     ('NSE', '4963'),
        'ICICI BANK':       ('NSE', '4963'),
        'HINDUNILVR':       ('NSE', '1394'),
        'ITC':              ('NSE', '1660'),
        'ITC-EQ':           ('NSE', '1660'),
        'SBIN':             ('NSE', '3045'),
        'SBIN-EQ':          ('NSE', '3045'),
        'SBI':              ('NSE', '3045'),
        'BHARTIARTL':       ('NSE', '10604'),
        'AIRTEL':           ('NSE', '10604'),
        'KOTAKBANK':        ('NSE', '1922'),
        'KOTAK':            ('NSE', '1922'),
        'LT':               ('NSE', '11483'),
        'LT-EQ':            ('NSE', '11483'),
        'AXISBANK':         ('NSE', '5900'),
        'AXISBANK-EQ':      ('NSE', '5900'),
        'BAJFINANCE':       ('NSE', '317'),
        'BAJFINANCE-EQ':    ('NSE', '317'),
        'WIPRO':            ('NSE', '3787'),
        'WIPRO-EQ':         ('NSE', '3787'),
        'HCLTECH':          ('NSE', '7229'),
        'ASIANPAINT':       ('NSE', '236'),
        'MARUTI':           ('NSE', '10999'),
        'MARUTI-EQ':        ('NSE', '10999'),
        'TITAN':            ('NSE', '3506'),
        'SUNPHARMA':        ('NSE', '3351'),
        'ULTRACEMCO':       ('NSE', '11532'),
        'NESTLEIND':        ('NSE', '17963'),
        'TATASTEEL':        ('NSE', '3499'),
        'TATASTEEL-EQ':     ('NSE', '3499'),
        'TATAMOTORS':       ('NSE', '3456'),
        'TATAMOTORS-EQ':    ('NSE', '3456'),
        'ONGC':             ('NSE', '2475'),
        'NTPC':             ('NSE', '11630'),
        'POWERGRID':        ('NSE', '14977'),
        'ADANIENT':         ('NSE', '25'),
        'ADANIPORTS':       ('NSE', '15083'),
        'TECHM':            ('NSE', '13538'),
        'JSWSTEEL':         ('NSE', '11723'),
        'DRREDDY':          ('NSE', '881'),
        'CIPLA':            ('NSE', '694'),
        'DIVISLAB':         ('NSE', '10940'),
        'APOLLOHOSP':       ('NSE', '157'),
        'BAJAJFINSV':       ('NSE', '16669'),
        'EICHERMOT':        ('NSE', '910'),
        'GRASIM':           ('NSE', '1232'),
        'HEROMOTOCO':       ('NSE', '1348'),
        'HINDALCO':         ('NSE', '1363'),
        'INDUSINDBK':       ('NSE', '5258'),
        'MM':               ('NSE', '2031'),
        'SBILIFE':          ('NSE', '21808'),
        'HDFCLIFE':         ('NSE', '467'),
        'BRITANNIA':        ('NSE', '547'),
        'BPCL':             ('NSE', '526'),
        'COALINDIA':        ('NSE', '20374'),
    }

    ANGEL_INTERVALS = {
        '1 Min':   'ONE_MINUTE',
        '3 Min':   'THREE_MINUTE',
        '5 Min':   'FIVE_MINUTE',
        '10 Min':  'TEN_MINUTE',
        '15 Min':  'FIFTEEN_MINUTE',
        '30 Min':  'THIRTY_MINUTE',
        '1 Hour':  'ONE_HOUR',
        '1 Day':   'ONE_DAY',
        '1 Week':  'ONE_WEEK',
        '1 Month': 'ONE_MONTH',
    }

    def _cred_file_path(self):
        import os
        return os.path.join(os.path.expanduser('~'), '.bulkowski_angel.cfg')

    def _save_credentials(self, api_key, client_id, password, totp_key):
        import base64, json
        try:
            data    = {'api_key': api_key, 'client_id': client_id,
                       'password': password, 'totp_key': totp_key}
            encoded = base64.b64encode(
                json.dumps(data).encode('utf-8')).decode('utf-8')
            path = self._cred_file_path()
            with open(path, 'w') as f:
                f.write(encoded)
            return True, path
        except Exception as e:
            return False, str(e)

    def _load_credentials(self):
        import base64, json, os
        try:
            path = self._cred_file_path()
            if not os.path.exists(path):
                return None
            with open(path, 'r') as f:
                encoded = f.read().strip()
            decoded = base64.b64decode(encoded.encode('utf-8')).decode('utf-8')
            return json.loads(decoded)
        except Exception:
            return None

    def _angel_connect(self, api_key, client_id, password, totp_key):
        """Connect to Angel One SmartAPI. Returns (success, message)."""
        try:
            from SmartApi import SmartConnect
            import pyotp

            obj = SmartConnect(api_key=api_key)

            # Generate TOTP
            if totp_key and totp_key.strip():
                totp_code = pyotp.TOTP(totp_key.strip()).now()
            else:
                totp_code = self._angel_manual_totp()
                if not totp_code:
                    return False, "TOTP cancelled"

            data = obj.generateSession(client_id, password, totp_code)

            if data and data.get('status'):
                session_data  = data.get('data', {})
                jwt_token     = session_data.get('jwtToken', '')
                refresh_token = session_data.get('refreshToken', '')
                feed_token    = session_data.get('feedToken', '')

                # Strip 'Bearer ' prefix if Angel One includes it
                if jwt_token.startswith('Bearer '):
                    jwt_token = jwt_token[7:]
                if refresh_token.startswith('Bearer '):
                    refresh_token = refresh_token[7:]

                # Set ALL tokens on the SmartConnect object
                obj.setAccessToken(jwt_token)
                try:    obj.setRefreshToken(refresh_token)
                except Exception: pass
                try:    obj.setFeedToken(feed_token)
                except Exception: pass
                try:    obj.setUserId(client_id)
                except Exception: pass

                self._angel_obj     = obj
                self._angel_token   = jwt_token
                self._angel_feed    = feed_token
                self._angel_refresh = refresh_token
                self._angel_uid     = client_id

                return True, f"Connected as {client_id}"
            else:
                msg = data.get('message', 'Unknown error') if data else 'No response'
                return False, f"Login failed: {msg}"

        except ImportError:
            return False, ("SmartAPI not installed.\n\n"
                           "Run in Spyder console:\n"
                           "import subprocess, sys\n"
                           "subprocess.check_call([sys.executable, '-m', 'pip',\n"
                           "'install', 'smartapi-python', 'pyotp', 'websocket-client'])")
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def _angel_manual_totp(self):
        """Ask user to enter TOTP manually."""
        win = tk.Toplevel(self.root)
        win.title("Enter TOTP")
        win.geometry('300x160')
        win.configure(bg='#1a1d23')
        win.grab_set()

        tk.Label(win, text="Enter 6-digit TOTP from\nGoogle Authenticator:",
                 bg='#1a1d23', fg='white',
                 font=('Consolas', 10)).pack(pady=12)

        var = tk.StringVar()
        entry = tk.Entry(win, textvariable=var, font=('Consolas', 18),
                         width=8, justify='center',
                         bg='#f0f0f0', fg='#1a1d23',
                         relief='flat')
        entry.pack(pady=4)
        entry.focus()

        result = [None]

        def ok():
            result[0] = var.get().strip()
            win.destroy()

        def cancel():
            win.destroy()

        btn_f = tk.Frame(win, bg='#1a1d23')
        btn_f.pack(pady=8)
        tk.Button(btn_f, text="OK", command=ok,
                  bg='#e67e22', fg='white',
                  font=('Consolas', 9, 'bold'),
                  padx=16, relief='flat').pack(side='left', padx=6)
        tk.Button(btn_f, text="Cancel", command=cancel,
                  bg='#555', fg='white',
                  font=('Consolas', 9), padx=10, relief='flat').pack(side='left')

        entry.bind('<Return>', lambda e: ok())
        win.wait_window()
        return result[0]

    def _angel_get_token(self, symbol_upper):
        """
        Get correct instrument token.
        Downloads Angel One official scrip master on first call, caches it.
        """
        import os, json

        # ── Load scrip master once per session ───────────────────────────
        if not hasattr(self, '_scrip_master') or not self._scrip_master:
            self._scrip_master = []
            import urllib.request, ssl
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode    = ssl.CERT_NONE
            urls = [
                'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json',
                'https://angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json',
            ]
            for url in urls:
                try:
                    req = urllib.request.Request(url, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                        'Accept': 'application/json, */*',
                    })
                    resp = urllib.request.urlopen(req, timeout=20, context=ctx)
                    raw  = resp.read()
                    try:
                        import gzip
                        raw = gzip.decompress(raw)
                    except Exception:
                        pass
                    self._scrip_master = json.loads(raw)
                    # Cache locally
                    try:
                        cache = os.path.join(os.path.expanduser("~"),
                                             ".bulkowski_scrip.json")
                        with open(cache, "w") as cf:
                            json.dump(self._scrip_master, cf)
                    except Exception:
                        pass
                    break
                except Exception:
                    continue
            # Try local cache if download failed
            if not self._scrip_master:
                try:
                    cache = os.path.join(os.path.expanduser("~"),
                                         ".bulkowski_scrip.json")
                    if os.path.exists(cache):
                        with open(cache) as cf:
                            self._scrip_master = json.load(cf)
                except Exception:
                    pass

        # ── Hardcoded index tokens ────────────────────────────────────────
        INDEX_TOKENS = {
            "NIFTY 50":     ("NSE", "99926000"),
            "NIFTY":        ("NSE", "99926000"),
            "NIFTY50":      ("NSE", "99926000"),
            "BANKNIFTY":    ("NSE", "99926009"),
            "BANK NIFTY":   ("NSE", "99926009"),
            "SENSEX":       ("BSE", "99919000"),
            "NIFTY IT":     ("NSE", "99926024"),
            "NIFTY AUTO":   ("NSE", "99926029"),
            "NIFTY PHARMA": ("NSE", "99926045"),
            "NIFTY FMCG":   ("NSE", "99926035"),
            "NIFTY METAL":  ("NSE", "99926037"),
            "NIFTY REALTY": ("NSE", "99926053"),
            "INDIA VIX":    ("NSE", "99926017"),
        }
        if symbol_upper in INDEX_TOKENS:
            return INDEX_TOKENS[symbol_upper]

        # ── Search scrip master ───────────────────────────────────────────
        sym_clean = symbol_upper.replace("-EQ", "").strip()
        if self._scrip_master:
            # Pass 1: exact name + NSE + EQ
            for item in self._scrip_master:
                if (item.get("name", "").upper() == sym_clean and
                        item.get("exch_seg", "") == "NSE" and
                        item.get("instrumenttype", "") == "EQ"):
                    return ("NSE", item["token"])
            # Pass 2: symbol field match
            for item in self._scrip_master:
                sf = item.get("symbol", "").upper()
                if (sf in (sym_clean, f"{sym_clean}-EQ") and
                        item.get("exch_seg", "") == "NSE"):
                    return ("NSE", item["token"])

        # ── searchScrip fallback ──────────────────────────────────────────
        try:
            for exch in ["NSE", "BSE"]:
                res = self._angel_obj.searchScrip(exch, sym_clean)
                if res and res.get("data"):
                    for item in res["data"]:
                        if item.get("instrumenttype", "").upper() == "EQ":
                            return (exch, item["symboltoken"])
                    return (exch, res["data"][0]["symboltoken"])
        except Exception:
            pass

        return None, None

    def _angel_fetch_data(self, symbol, interval_label, from_date, to_date):
        """
        Fetch OHLCV using ONLY direct HTTP — bypasses SmartAPI library.
        This is the method confirmed working from debug test.
        Works for: indices, stocks, ETFs.
        For options (CE/PE): use _angel_fetch_options instead.
        """
        try:
            import urllib.request, json as _json, ssl

            symbol_upper = symbol.strip().upper()
            interval     = self.ANGEL_INTERVALS.get(interval_label, 'ONE_DAY')
            jwt          = getattr(self, '_angel_token', '')
            api_key      = self._angel_config.get('api_key', 'gbjChoIy')
            is_intraday  = interval not in ('ONE_DAY', 'ONE_WEEK', 'ONE_MONTH')
            from_time    = '09:15' if is_intraday else '09:00'

            # Normalize dates to strict YYYY-MM-DD (zero-padded) — Angel One returns
            # HTTP 400 if dates have single-digit month/day (e.g. "2026-4-2").
            import datetime as _dt
            from_date = _dt.datetime.strptime(str(from_date).strip(), '%Y-%m-%d').strftime('%Y-%m-%d')
            to_date   = _dt.datetime.strptime(str(to_date).strip(),   '%Y-%m-%d').strftime('%Y-%m-%d')

            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode    = ssl.CERT_NONE

            base_headers = {
                'Content-Type':    'application/json',
                'Accept':          'application/json',
                'X-UserType':      'USER',
                'X-SourceID':      'WEB',
                'X-ClientLocalIP': '127.0.0.1',
                'X-ClientPublicIP':'127.0.0.1',
                'X-MACAddress':    '00:00:00:00:00:00',
                'X-PrivateKey':    api_key,
                'Authorization':   f'Bearer {jwt}',
            }
            # Use preset map first (fastest, no API call needed)
            preset = self.ANGEL_TOKENS.get(symbol_upper)
            if preset:
                exchange, token = preset
            else:
                # Search via direct HTTP
                exchange, token = None, None
                try:
                    search_url  = ('https://apiconnect.angelone.in/rest/secure/'
                                   'angelbroking/order/v1/searchScrip')
                    search_body = _json.dumps({
                        'exchange': 'NSE',
                        'searchscrip': symbol_upper
                    }).encode()
                    req  = urllib.request.Request(
                        search_url, data=search_body,
                        headers=base_headers, method='POST')
                    resp = urllib.request.urlopen(req, timeout=10, context=ctx)
                    data = _json.loads(resp.read())
                    if data.get('status') and data.get('data'):
                        for item in data['data']:
                            ts    = item.get('tradingsymbol', '').upper()
                            itype = item.get('instrumenttype', '').upper()
                            if ts == symbol_upper and itype == 'EQ':
                                token    = item.get('symboltoken', '')
                                exchange = 'NSE'
                                break
                        if not token and data['data']:
                            token    = data['data'][0].get('symboltoken', '')
                            exchange = 'NSE'
                except Exception:
                    pass

            if not token:
                return None, (
                    f"Symbol \'{symbol_upper}\' not found.\n\n"
                    f"Try these exact names:\n"
                    f"  Indices: NIFTY 50, BANKNIFTY, SENSEX\n"
                    f"  Stocks:  RELIANCE, TCS, HDFCBANK, INFY, SBIN\n"
                    f"  Options: NIFTY25APR2424000CE (auto-routes to NFO)"
                )

            # ── Step 2: Fetch OHLCV via direct HTTP ──────────────────────
            candle_url  = ('https://apiconnect.angelone.in/rest/secure/'
                           'angelbroking/historical/v1/getCandleData')
            candle_body = _json.dumps({
                'exchange':    exchange,
                'symboltoken': str(token),
                'interval':    interval,
                'fromdate':    f"{from_date} {from_time}",
                'todate':      f"{to_date} 15:30",
            }).encode()

            req  = urllib.request.Request(
                candle_url, data=candle_body,
                headers=base_headers, method='POST')
            resp = urllib.request.urlopen(req, timeout=15, context=ctx)
            raw  = _json.loads(resp.read())

            if not raw.get('status'):
                return None, f"API error: {raw.get('message', 'Unknown error')}"

            raw_data = raw.get('data', [])
            if not raw_data:
                return None, (
                    f"No data for {symbol_upper} ({from_date} to {to_date}).\n"
                    f"Try a wider date range."
                )

            # ── Step 3: Parse into DataFrame ─────────────────────────────
            rows = []
            for bar in raw_data:
                try:
                    rows.append({
                        'Date':   str(bar[0])[:10],
                        'Open':   float(bar[1]),
                        'High':   float(bar[2]),
                        'Low':    float(bar[3]),
                        'Close':  float(bar[4]),
                        'Volume': int(float(bar[5])) if len(bar) > 5 else 0,
                    })
                except Exception:
                    continue

            if not rows:
                return None, "Data received but could not be parsed."

            df = pd.DataFrame(rows)
            df['Date'] = pd.to_datetime(df['Date'])
            df.sort_values('Date', ascending=True, inplace=True)
            df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
            df.reset_index(drop=True, inplace=True)

            return df, (f"✅ {len(df)} bars  |  {symbol_upper} ({interval_label})  |  "
                        f"Exchange: {exchange}  Token: {token}")

        except Exception as e:
            return None, f"Fetch error: {str(e)}"

    def _angel_fetch_options(self, symbol, interval_label, from_date, to_date):
        """
        Fetch OHLCV for options contracts (CE/PE) from Angel One NFO segment.
        Uses only direct HTTP — no SmartAPI library calls.

        Format: NIFTY25APR2424000CE / BANKNIFTY25APR2448000CE / RELIANCE25APR241400CE
        """
        try:
            import urllib.request, json as _json, ssl

            symbol_upper = symbol.strip().upper()
            interval     = self.ANGEL_INTERVALS.get(interval_label, 'ONE_DAY')
            jwt          = getattr(self, '_angel_token', '')
            api_key      = self._angel_config.get('api_key', 'gbjChoIy')
            is_intraday  = interval not in ('ONE_DAY', 'ONE_WEEK', 'ONE_MONTH')
            from_time    = '09:15' if is_intraday else '09:00'

            # Normalize dates to strict YYYY-MM-DD (zero-padded)
            import datetime as _dt
            from_date = _dt.datetime.strptime(str(from_date).strip(), '%Y-%m-%d').strftime('%Y-%m-%d')
            to_date   = _dt.datetime.strptime(str(to_date).strip(),   '%Y-%m-%d').strftime('%Y-%m-%d')

            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode    = ssl.CERT_NONE

            base_headers = {
                'Content-Type':    'application/json',
                'Accept':          'application/json',
                'X-UserType':      'USER',
                'X-SourceID':      'WEB',
                'X-ClientLocalIP': '127.0.0.1',
                'X-ClientPublicIP':'127.0.0.1',
                'X-MACAddress':    '00:00:00:00:00:00',
                'X-PrivateKey':    api_key,
                'Authorization':   f'Bearer {jwt}',
            }

            # ── Step 1: Search for options token ─────────────────────────
            token    = None
            exchange = 'NFO'

            # Load scrip master from disk cache if not in memory
            if not hasattr(self, '_scrip_master') or not self._scrip_master:
                try:
                    import os
                    cache = os.path.join(os.path.expanduser('~'),
                                         '.bulkowski_scrip.json')
                    if os.path.exists(cache):
                        with open(cache) as cf:
                            self._scrip_master = _json.load(cf)
                except Exception:
                    pass

            # Search scrip master for NFO symbol match
            if self._scrip_master:
                # Pass 1: exact match
                for item in self._scrip_master:
                    sf   = item.get('symbol', '').upper()
                    exch = item.get('exch_seg', '')
                    if exch == 'NFO' and sf == symbol_upper:
                        token    = item['token']
                        exchange = 'NFO'
                        break

                # Pass 2: if not found, try stripping leading zeros from strike
                # e.g. NIFTY28APR2623900CE might be stored as NIFTY28APR2623900CE
                if not token:
                    import re as _re
                    m = _re.match(r'^([A-Z]+)(\d{2}[A-Z]{3}\d{2})(\d+)(CE|PE)$',
                                  symbol_upper)
                    if m:
                        # Try with strike as-is and without leading zeros
                        strike_variants = [
                            m.group(3),
                            str(int(m.group(3))),  # remove leading zeros
                        ]
                        for sv in strike_variants:
                            alt = f"{m.group(1)}{m.group(2)}{sv}{m.group(4)}"
                            for item in self._scrip_master:
                                sf   = item.get('symbol', '').upper()
                                exch = item.get('exch_seg', '')
                                if exch == 'NFO' and sf == alt:
                                    token    = item['token']
                                    exchange = 'NFO'
                                    symbol_upper = alt  # use the found symbol
                                    break
                            if token:
                                break

            # If not found in scrip master, try direct HTTP searchScrip
            if not token:
                try:
                    search_url  = ('https://apiconnect.angelone.in/rest/secure/'
                                   'angelbroking/order/v1/searchScrip')
                    search_body = _json.dumps({
                        'exchange':    'NFO',
                        'searchscrip': symbol_upper
                    }).encode()
                    req  = urllib.request.Request(
                        search_url, data=search_body,
                        headers=base_headers, method='POST')
                    resp = urllib.request.urlopen(req, timeout=10, context=ctx)
                    raw_text = resp.read().decode('utf-8', errors='replace')
                    data = _json.loads(raw_text)
                    if data.get('status') and data.get('data'):
                        for item in data['data']:
                            ts = item.get('tradingsymbol', '').upper()
                            if ts == symbol_upper:
                                token    = item.get('symboltoken', '')
                                exchange = 'NFO'
                                break
                        if not token and data['data']:
                            token    = data['data'][0].get('symboltoken', '')
                            exchange = 'NFO'
                except Exception:
                    pass

            if not token:
                return None, (
                    f"Token not found for '{symbol_upper}'.\n\n"
                    f"To fetch options data:\n"
                    f"1. Click '📋 Get Options Tokens' button first\n"
                    f"   (downloads instrument list — one-time, ~15MB)\n"
                    f"2. Then fetch any options symbol\n\n"
                    f"Format: NIFTY25APR2424000CE\n"
                    f"        (SYMBOL + DDMMMYY + STRIKE + CE/PE)"
                )

                        # ── Step 2: Fetch OHLCV via direct HTTP ──────────────────────
            candle_url  = ('https://apiconnect.angelone.in/rest/secure/'
                           'angelbroking/historical/v1/getCandleData')
            candle_body = _json.dumps({
                'exchange':    'NFO',
                'symboltoken': str(token),
                'interval':    interval,
                'fromdate':    f"{from_date} {from_time}",
                'todate':      f"{to_date} 15:30",
            }).encode()

            req  = urllib.request.Request(
                candle_url, data=candle_body,
                headers=base_headers, method='POST')
            resp = urllib.request.urlopen(req, timeout=15, context=ctx)
            raw  = _json.loads(resp.read())

            if not raw.get('status'):
                return None, (
                    f"Fetch failed: {raw.get('message', 'Unknown error')}\n"
                    f"Token: {token}  Symbol: {symbol_upper}"
                )

            raw_data = raw.get('data', [])
            if not raw_data:
                return None, (
                    f"No OHLC data for {symbol_upper}.\n\n"
                    f"Possible reasons:\n"
                    f"1. Contract not traded in this date range\n"
                    f"2. Try last 1-2 weeks before expiry (most active period)\n"
                    f"3. For intraday: select 5 Min or 15 Min timeframe"
                )

            # ── Step 3: Parse ─────────────────────────────────────────────
            rows = []
            for bar in raw_data:
                try:
                    rows.append({
                        'Date':   str(bar[0])[:10],
                        'Open':   float(bar[1]),
                        'High':   float(bar[2]),
                        'Low':    float(bar[3]),
                        'Close':  float(bar[4]),
                        'Volume': int(float(bar[5])) if len(bar) > 5 else 0,
                    })
                except Exception:
                    continue

            if not rows:
                return None, "Data received but could not be parsed."

            df = pd.DataFrame(rows)
            df['Date'] = pd.to_datetime(df['Date'])
            df.sort_values('Date', ascending=True, inplace=True)
            df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
            df.reset_index(drop=True, inplace=True)

            return df, (f"✅ {len(df)} bars  |  {symbol_upper}  |  NFO  |  Token: {token}")

        except Exception as e:
            return None, f"Options fetch error: {str(e)}"

    def _show_angel_one(self):
        """Angel One SmartAPI connection and data fetch window."""
        try:
            self._build_angel_one_window()
        except Exception as e:
            import traceback
            messagebox.showerror("Angel One Error",
                f"Could not open Angel One window:\n\n{str(e)}\n\n"
                f"{traceback.format_exc()[-400:]}")

    def _build_angel_one_window(self):
        AO_COL  = '#e67e22'
        AO_DARK = '#7d3a00'

        # ── Auto-load saved credentials ──────────────────────────────────
        saved = self._load_credentials()
        if saved:
            self._angel_config.update({
                k: saved.get(k, self._angel_config.get(k, ''))
                for k in ('api_key', 'client_id', 'password', 'totp_key')
            })

        win = tk.Toplevel(self.root)
        win.title("🔌 Angel One SmartAPI — Data Fetcher")
        win.geometry('640x820')
        win.configure(bg='#f5f5f5')
        win.resizable(True, True)

        # ── HEADER ──────────────────────────────────────────────────────────
        hdr = tk.Frame(win, bg='#1a1d23', pady=10, padx=16)
        hdr.pack(fill='x')
        tk.Label(hdr, text="🔌  ANGEL ONE SMARTAPI",
                 bg='#1a1d23', fg=AO_COL,
                 font=('Consolas', 13, 'bold')).pack(side='left')

        # Connection status
        self._ao_status_var = tk.StringVar(
            value="● NOT CONNECTED" if not self._angel_obj else "● CONNECTED")
        status_col = '#e74c3c' if not self._angel_obj else '#2ecc71'
        self._ao_status_lbl = tk.Label(hdr, textvariable=self._ao_status_var,
                                        bg='#1a1d23', fg=status_col,
                                        font=('Consolas', 9, 'bold'))
        self._ao_status_lbl.pack(side='right')

        # ── CREDENTIALS SECTION ─────────────────────────────────────────────
        cred_frame = tk.LabelFrame(win, text="  Login Credentials  ",
                                    bg='#f5f5f5', fg=AO_DARK,
                                    font=('Consolas', 9, 'bold'),
                                    relief='groove', bd=2,
                                    padx=16, pady=10)
        cred_frame.pack(fill='x', padx=16, pady=10)

        fields_cfg = [
            ('API Key',         'api_key',   False, 'gbjChoIy'),
            ('Client ID',       'client_id', False, 'Your Angel One Login ID'),
            ('Password',        'password',  True,  ''),
            ('TOTP Secret Key', 'totp_key',  True,
             'From Google Auth setup — leave blank to enter manually each time'),
        ]

        self._ao_vars = {}
        for label, key, is_secret, placeholder in fields_cfg:
            row = tk.Frame(cred_frame, bg='#f5f5f5')
            row.pack(fill='x', pady=3)
            tk.Label(row, text=f"{label}:", bg='#f5f5f5', fg='#333',
                     font=('Consolas', 9), width=18, anchor='w').pack(side='left')
            var = tk.StringVar(value=self._angel_config.get(key, ''))
            if key == 'api_key':
                var.set('gbjChoIy')
            e = tk.Entry(row, textvariable=var,
                         show='*' if is_secret else '',
                         bg='#ffffff', fg='#1a1d23',
                         font=('Consolas', 9), relief='solid', bd=1,
                         width=32)
            e.pack(side='left', padx=6)
            self._ao_vars[key] = var
            if placeholder and not is_secret:
                e.insert(0, '')

        # Help text for TOTP
        tk.Label(cred_frame,
                 text="ℹ  TOTP Secret Key: Found in Google Auth QR setup for Angel One.\n"
                      "   Leave blank → app will ask you to type 6-digit code at login.",
                 bg='#f5f5f5', fg='#888', font=('Consolas', 7),
                 justify='left').pack(anchor='w', pady=2)

        # Connect button
        def do_connect():
            api_k = self._ao_vars['api_key'].get().strip()
            cid   = self._ao_vars['client_id'].get().strip()
            pwd   = self._ao_vars['password'].get().strip()
            totp  = self._ao_vars['totp_key'].get().strip()

            if not cid or not pwd:
                messagebox.showwarning("Missing", "Please enter Client ID and Password.", parent=win)
                return

            # Save config
            self._angel_config.update({
                'api_key': api_k, 'client_id': cid,
                'password': pwd, 'totp_key': totp
            })

            self._ao_status_var.set("⏳ Connecting...")
            self._ao_status_lbl.config(fg='#f1c40f')
            win.update()

            ok, msg = self._angel_connect(api_k, cid, pwd, totp)
            if ok:
                self._ao_status_var.set("● CONNECTED")
                self._ao_status_lbl.config(fg='#2ecc71')
                self.status_var.set(f"🔌 Angel One: {msg}")
                # Auto-save credentials on successful connection
                self._save_credentials(api_k, cid, pwd, totp)

                # Check profile and permissions
                profile_info = ""
                try:
                    prof = self._angel_obj.getProfile(
                        self._angel_refresh)
                    if prof and prof.get('status'):
                        pd = prof.get('data', {})
                        profile_info = (
                            f"\n\nProfile: {pd.get('name','?')}"
                            f"\nEmail: {pd.get('email','?')}"
                            f"\nBroker: {pd.get('broker','?')}"
                            f"\nExchanges: {pd.get('exchanges',[])} "
                            f"\nProducts: {pd.get('products',[])}"
                        )
                except Exception as pe:
                    profile_info = f"\n\nProfile check: {str(pe)[:60]}"

                messagebox.showinfo("Connected!", msg + profile_info, parent=win)
            else:
                self._ao_status_var.set("● FAILED")
                self._ao_status_lbl.config(fg='#e74c3c')
                messagebox.showerror("Connection Failed", msg, parent=win)

        tk.Button(cred_frame, text="🔌  CONNECT TO ANGEL ONE",
                  command=do_connect,
                  bg=AO_COL, fg='white',
                  font=('Consolas', 10, 'bold'),
                  relief='flat', padx=16, pady=6,
                  cursor='hand2').pack(pady=6)

        # ── Save / Clear credential buttons ─────────────────────────────────
        save_row = tk.Frame(cred_frame, bg='#f5f5f5')
        save_row.pack(pady=2)

        def do_save():
            api_k = self._ao_vars['api_key'].get().strip()
            cid   = self._ao_vars['client_id'].get().strip()
            pwd   = self._ao_vars['password'].get().strip()
            totp  = self._ao_vars['totp_key'].get().strip()
            if not cid:
                messagebox.showwarning("Missing",
                    "Enter Client ID before saving.", parent=win)
                return
            ok, path = self._save_credentials(api_k, cid, pwd, totp)
            if ok:
                messagebox.showinfo("Saved!",
                    f"✅ Credentials saved to:\n{path}\n\n"
                    f"They will auto-load next time you open this window.\n\n"
                    f"⚠ Keep this file private — do not share it.",
                    parent=win)
            else:
                messagebox.showerror("Save Failed",
                    f"Could not save: {path}", parent=win)

        def do_clear():
            if messagebox.askyesno("Clear Saved Credentials",
                "Delete saved credentials from disk?\n"
                "You will need to enter them again next time.",
                parent=win):
                import os
                path = self._cred_file_path()
                try:
                    if os.path.exists(path):
                        os.remove(path)
                    # Clear fields
                    for key in ('client_id', 'password', 'totp_key'):
                        self._ao_vars[key].set('')
                    messagebox.showinfo("Cleared",
                        "Saved credentials deleted.", parent=win)
                except Exception as e:
                    messagebox.showerror("Error", str(e), parent=win)

        # Check if saved file exists
        import os
        cred_path = self._cred_file_path()
        saved_exists = os.path.exists(cred_path)
        save_status  = "✅ Credentials saved on disk" if saved_exists else "○ No saved credentials"
        save_col     = '#27ae60' if saved_exists else '#888'

        save_status_lbl = tk.Label(save_row,
                                    text=save_status,
                                    bg='#f5f5f5', fg=save_col,
                                    font=('Consolas', 8))
        save_status_lbl.pack(side='left', padx=8)

        tk.Button(save_row, text="💾 Save Credentials",
                  command=do_save,
                  bg='#27ae60', fg='white',
                  font=('Consolas', 8, 'bold'),
                  relief='flat', padx=10, pady=4,
                  cursor='hand2').pack(side='left', padx=4)

        tk.Button(save_row, text="🗑 Clear Saved",
                  command=do_clear,
                  bg='#e74c3c', fg='white',
                  font=('Consolas', 8, 'bold'),
                  relief='flat', padx=10, pady=4,
                  cursor='hand2').pack(side='left', padx=4)

        # ── DATA FETCH SECTION ───────────────────────────────────────────────
        fetch_frame = tk.LabelFrame(win, text="  Fetch Chart Data  ",
                                     bg='#f5f5f5', fg=AO_DARK,
                                     font=('Consolas', 9, 'bold'),
                                     relief='groove', bd=2,
                                     padx=16, pady=10)
        fetch_frame.pack(fill='x', padx=16, pady=6)

        # Symbol search
        row1 = tk.Frame(fetch_frame, bg='#f5f5f5')
        row1.pack(fill='x', pady=4)
        tk.Label(row1, text="Symbol / Index:", bg='#f5f5f5', fg='#333',
                 font=('Consolas', 9), width=18, anchor='w').pack(side='left')
        sym_var = tk.StringVar(value='NIFTY 50')
        sym_entry = tk.Entry(row1, textvariable=sym_var,
                             bg='#ffffff', fg='#1a1d23',
                             font=('Consolas', 10), relief='solid', bd=1,
                             width=22)
        sym_entry.pack(side='left', padx=6)

        # Quick symbol buttons
        quick_frame = tk.Frame(fetch_frame, bg='#f5f5f5')
        quick_frame.pack(fill='x', pady=2)
        tk.Label(quick_frame, text="Quick:", bg='#f5f5f5', fg='#888',
                 font=('Consolas', 8), width=18, anchor='w').pack(side='left')
        for sym in ['NIFTY 50', 'BANKNIFTY', 'RELIANCE', 'TCS', 'HDFCBANK',
                    'INFY', 'SBIN', 'ICICIBANK']:
            tk.Button(quick_frame, text=sym,
                      command=lambda s=sym: sym_var.set(s),
                      bg='#e8e8e8', fg='#333',
                      font=('Consolas', 7), relief='flat',
                      padx=4, pady=2, cursor='hand2').pack(side='left', padx=2)

        # Interval
        row2 = tk.Frame(fetch_frame, bg='#f5f5f5')
        row2.pack(fill='x', pady=4)
        tk.Label(row2, text="Timeframe:", bg='#f5f5f5', fg='#333',
                 font=('Consolas', 9), width=18, anchor='w').pack(side='left')
        intv_var = tk.StringVar(value='1 Day')
        intv_menu = ttk.Combobox(row2, textvariable=intv_var,
                                  values=list(self.ANGEL_INTERVALS.keys()),
                                  width=12, state='readonly',
                                  font=('Consolas', 9))
        intv_menu.pack(side='left', padx=6)

        # Date range
        row3 = tk.Frame(fetch_frame, bg='#f5f5f5')
        row3.pack(fill='x', pady=4)
        tk.Label(row3, text="From Date:", bg='#f5f5f5', fg='#333',
                 font=('Consolas', 9), width=18, anchor='w').pack(side='left')
        from_var = tk.StringVar(value='2026-01-01')
        tk.Entry(row3, textvariable=from_var,
                 bg='#ffffff', fg='#1a1d23',
                 font=('Consolas', 9), relief='solid', bd=1,
                 width=14).pack(side='left', padx=6)

        row4 = tk.Frame(fetch_frame, bg='#f5f5f5')
        row4.pack(fill='x', pady=4)
        tk.Label(row4, text="To Date:", bg='#f5f5f5', fg='#333',
                 font=('Consolas', 9), width=18, anchor='w').pack(side='left')
        import datetime
        to_var = tk.StringVar(value=datetime.date.today().strftime('%Y-%m-%d'))
        tk.Entry(row4, textvariable=to_var,
                 bg='#ffffff', fg='#1a1d23',
                 font=('Consolas', 9), relief='solid', bd=1,
                 width=14).pack(side='left', padx=6)

        # Quick date buttons
        date_frame = tk.Frame(fetch_frame, bg='#f5f5f5')
        date_frame.pack(fill='x', pady=2)
        tk.Label(date_frame, text="Quick range:", bg='#f5f5f5', fg='#888',
                 font=('Consolas', 8), width=18, anchor='w').pack(side='left')

        def set_range(days):
            today = datetime.date.today()
            from_var.set((today - datetime.timedelta(days=days)).strftime('%Y-%m-%d'))
            to_var.set(today.strftime('%Y-%m-%d'))

        for label, days in [('1M', 30), ('3M', 90), ('6M', 180), ('1Y', 365)]:
            tk.Button(date_frame, text=label,
                      command=lambda d=days: set_range(d),
                      bg='#e8e8e8', fg='#333',
                      font=('Consolas', 8), relief='flat',
                      padx=8, pady=2, cursor='hand2').pack(side='left', padx=2)

        # Target: Daily or Intraday chart
        row5 = tk.Frame(fetch_frame, bg='#f5f5f5')
        row5.pack(fill='x', pady=4)
        tk.Label(row5, text="Load into:", bg='#f5f5f5', fg='#333',
                 font=('Consolas', 9), width=18, anchor='w').pack(side='left')
        target_var = tk.StringVar(value='1D Chart')
        for lbl in ['1D Chart', 'Intraday Chart']:
            tk.Radiobutton(row5, text=lbl, value=lbl,
                           variable=target_var,
                           bg='#f5f5f5', fg='#333',
                           font=('Consolas', 9),
                           activebackground='#f5f5f5').pack(side='left', padx=8)

        # ── Fetch result log ─────────────────────────────────────────────────
        log_var = tk.StringVar(value="Connect to Angel One, then fetch data.")
        log_lbl = tk.Label(fetch_frame, textvariable=log_var,
                            bg='#fff8ee', fg='#555',
                            font=('Consolas', 8),
                            anchor='w', padx=8, pady=4,
                            wraplength=540, justify='left')
        log_lbl.pack(fill='x', pady=4)

        def is_options_symbol(sym):
            # Options symbols always end with CE or PE
            return sym.endswith('CE') or sym.endswith('PE')

        def do_fetch():
            if not self._angel_obj:
                messagebox.showwarning("Not Connected",
                    "Please connect to Angel One first.", parent=win)
                return
            sym   = sym_var.get().strip().upper()
            intv  = intv_var.get()
            fdate = from_var.get().strip()
            tdate = to_var.get().strip()
            tgt   = target_var.get()
            if not sym:
                messagebox.showwarning("Missing", "Enter a symbol.", parent=win)
                return
            log_var.set(f"⏳ Fetching {sym} ({intv}) {fdate} → {tdate}...")
            log_lbl.config(fg='#e67e22')
            win.update()
            if is_options_symbol(sym):
                df, msg = self._angel_fetch_options(sym, intv, fdate, tdate)
            else:
                df, msg = self._angel_fetch_data(sym, intv, fdate, tdate)
            if df is None:
                log_var.set(f"❌ {msg}")
                log_lbl.config(fg='#e74c3c')
                messagebox.showerror("Fetch Failed", msg, parent=win)
                return
            log_var.set(f"✅ {msg}")
            log_lbl.config(fg='#27ae60')
            if tgt == '1D Chart':
                self.df = df
                self.detected = []
                self.brooks_signals = []
                self.quant_signals  = []
                self.street_smarts  = []
                draw_chart(self.fig, self.df, [])
                self.canvas.draw()
                self._setup_crosshair()
                self._switch_tab('daily')
                self.status_var.set(f"🔌 {sym} {intv} loaded ({len(df)} bars) — click Detect")
                messagebox.showinfo("Loaded!",
                    f"{sym} ({intv})\n{len(df)} bars loaded into Daily Chart.\n\nClick 🔍 Detect.", parent=win)
            else:
                self.df_intra = df
                # Auto-scroll to latest bars on load
                self._intra_window_size = min(120, len(df))
                self._intra_offset = max(0, len(df) - self._intra_window_size)
                self._intra_status.config(text=f"  ✅ {sym} — {len(df)} bars", fg='#1abc9c')
                self._draw_intraday_chart()
                self._switch_tab('intraday')
                self.status_var.set(f"🔌 {sym} {intv} — {len(df)} bars in Intraday chart")

        def do_token_lookup():
            """Look up and show the token for the entered symbol."""
            if not self._angel_obj:
                messagebox.showwarning("Not Connected", "Connect first.", parent=win)
                return
            sym = sym_var.get().strip().upper()
            if not sym:
                return
            log_var.set(f"🔍 Looking up token for {sym}...")
            log_lbl.config(fg='#e67e22')
            win.update()
            exch, tok = self._angel_get_token(sym)
            if tok:
                log_var.set(f"✅ Found: {sym} → Exchange={exch}  Token={tok}")
                log_lbl.config(fg='#27ae60')
            else:
                log_var.set(f"❌ Token not found for {sym}")
                log_lbl.config(fg='#e74c3c')

        def do_debug_test():
            """Test all exchange+token combos and show searchScrip results."""
            if not self._angel_obj:
                messagebox.showwarning("Not Connected", "Connect first.", parent=win)
                return

            sym = sym_var.get().strip().upper()
            log_var.set(f"🔬 Running diagnostics for {sym}...")
            log_lbl.config(fg='#e67e22')
            win.update()

            results = []
            interval = self.ANGEL_INTERVALS.get(intv_var.get(), 'ONE_DAY')
            fd = '2026-04-01 09:00'
            td = '2026-04-25 15:30'

            # 0. Check session validity
            results.append("=== Session / Profile Check ===")
            try:
                prof = self._angel_obj.getProfile(
                    getattr(self, '_angel_refresh', ''))
                if prof and prof.get('status'):
                    pd = prof.get('data', {})
                    results.append(f"  Name:      {pd.get('name','?')}")
                    results.append(f"  Exchanges: {pd.get('exchanges',[])} ")
                    results.append(f"  Products:  {pd.get('products',[])} ")
                    results.append(f"  Broker:    {pd.get('broker','?')}")
                else:
                    results.append(f"  Profile failed: {prof.get('message','?') if prof else 'no response'}")
            except Exception as e:
                results.append(f"  Profile error: {str(e)[:60]}")

            results.append(f"  JWT token: {getattr(self,'_angel_token','?')[:40]}...")
            results.append("")

            results.append("")
            results.append("=== Direct HTTP Test (bypass library) ===")
            try:
                import urllib.request, json as _json, ssl
                jwt = getattr(self, '_angel_token', '')
                api_key = self._angel_config.get('api_key', 'gbjChoIy')

                # Direct REST call — use actual symbol token, not hardcoded RELIANCE
                # Get token for the symbol being tested
                _test_exch, _test_tok = self._angel_get_token(sym)
                _test_tok  = _test_tok  or '2885'
                _test_exch = _test_exch or 'NSE'

                url  = ('https://apiconnect.angelone.in/rest/secure/'
                        'angelbroking/historical/v1/getCandleData')
                body = _json.dumps({
                    'exchange':    _test_exch,
                    'symboltoken': str(_test_tok),
                    'interval':    'ONE_DAY',
                    'fromdate':    '2026-04-01 09:00',
                    'todate':      '2026-04-25 15:30',
                }).encode('utf-8')

                headers = {
                    'Content-Type':  'application/json',
                    'Accept':        'application/json',
                    'X-UserType':    'USER',
                    'X-SourceID':    'WEB',
                    'X-ClientLocalIP': '127.0.0.1',
                    'X-ClientPublicIP': '127.0.0.1',
                    'X-MACAddress':  '00:00:00:00:00:00',
                    'X-PrivateKey':  api_key,
                    'Authorization': f'Bearer {jwt}',
                }
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode    = ssl.CERT_NONE
                req  = urllib.request.Request(url, data=body,
                                              headers=headers, method='POST')
                resp = urllib.request.urlopen(req, timeout=15, context=ctx)
                raw  = _json.loads(resp.read())
                if raw.get('status') and raw.get('data'):
                    results.append(f"  ✅ DIRECT HTTP WORKS! {len(raw['data'])} bars")
                else:
                    results.append(f"  ❌ Direct HTTP: {raw.get('message','?')[:60]}")
            except Exception as e:
                results.append(f"  ❌ Direct HTTP error: {str(e)[:80]}")
            results.append("")
            for exch in ['NSE', 'BSE', 'NFO']:
                try:
                    res = self._angel_obj.searchScrip(exch, sym)
                    if res and res.get('data'):
                        for item in res['data'][:3]:
                            results.append(
                                f"  [{exch}] symbol={item.get('tradingsymbol','')} "
                                f"token={item.get('symboltoken','')} "
                                f"type={item.get('instrumenttype','')}")
                    else:
                        results.append(f"  [{exch}] No results")
                except Exception as e:
                    results.append(f"  [{exch}] Error: {str(e)[:40]}")

            results.append("")
            results.append("=== getCandleData Tests ===")

            # Test with actual symbol's token FIRST
            test_combos = []
            actual_exch, actual_tok = self._angel_get_token(sym)
            if actual_tok:
                test_combos.append((actual_exch or 'NSE', actual_tok,
                                    f"{sym} (looked up token)"))
                # Also try NFO for options
                if sym.endswith('CE') or sym.endswith('PE'):
                    test_combos.append(('NFO', actual_tok,
                                        f"{sym} NFO exchange"))

            # Add tokens from searchScrip
            for exch in ['NSE', 'NFO', 'BSE']:
                try:
                    res = self._angel_obj.searchScrip(exch, sym)
                    if res and res.get('data'):
                        for item in res['data'][:2]:
                            tok = item.get('symboltoken', '')
                            ts  = item.get('tradingsymbol', '')
                            test_combos.append(
                                (exch, tok, f"searchScrip {exch} {ts}"))
                except Exception:
                    pass

            # Add hardcoded known-good tokens just to verify API works
            test_combos += [
                ('NSE', '2885',     'RELIANCE (API health check)'),
                ('NSE', '99926000', 'NIFTY 50 (API health check)'),
            ]

            for exch, token, label in test_combos[:8]:
                try:
                    params = {
                        'exchange':    exch,
                        'symboltoken': str(token),
                        'interval':    interval,
                        'fromdate':    fd,
                        'todate':      td,
                    }
                    resp = self._angel_obj.getCandleData(params)
                    if resp and resp.get('status') and resp.get('data'):
                        n = len(resp['data'])
                        results.append(
                            f"✅ WORKS! exch={exch} token={token} → {n} bars  [{label}]")
                    elif resp:
                        msg = resp.get('message', '?')[:50]
                        results.append(
                            f"❌ {msg}  exch={exch} token={token}  [{label}]")
                    else:
                        results.append(f"❌ No resp  exch={exch} token={token}")
                except Exception as e:
                    results.append(f"❌ Exc: {str(e)[:40]}  [{label}]")

            result_text = '\n'.join(results)

            # Show results window
            res_win = tk.Toplevel(win)
            res_win.title(f"Debug Results — {sym}")
            res_win.geometry('680x420')
            res_win.configure(bg='#1a1d23')
            tk.Label(res_win, text=f"Debug Test Results for {sym}",
                     bg='#1a1d23', fg='#f1c40f',
                     font=('Consolas', 10, 'bold'), pady=8).pack()
            tk.Label(res_win,
                     text="Share a screenshot of this window so the correct token can be identified.",
                     bg='#1a1d23', fg='#888',
                     font=('Consolas', 8)).pack()
            import tkinter.scrolledtext as _st
            txt = _st.ScrolledText(res_win, bg='#0d1117', fg='#c9d1d9',
                                   font=('Consolas', 9), wrap=tk.WORD,
                                   padx=10, pady=8)
            txt.pack(fill='both', expand=True, padx=8, pady=4)
            txt.tag_config('good', foreground='#2ecc71')
            txt.tag_config('bad',  foreground='#e74c3c')
            txt.tag_config('hdr',  foreground='#f1c40f')
            for line in results:
                tag = 'good' if line.startswith('✅') else \
                      ('bad'  if line.startswith('❌') else \
                      ('hdr'  if line.startswith('===') else None))
                txt.insert('end', line + '\n', tag or '')
            txt.config(state='disabled')

            worked = [r for r in results if r.startswith('✅')]
            if worked:
                log_var.set(f"✅ Working combo found! Check debug window.")
                log_lbl.config(fg='#27ae60')
                # Only cache the result if it actually matches our symbol
                # Don't cache hardcoded test tokens for wrong symbols
                for w in worked:
                    import re as _re2
                    m = _re2.search(r'exch=(\w+)\s+token=(\w+)', w)
                    if m:
                        w_exch, w_tok = m.group(1), m.group(2)
                        # Only cache if the label mentions our actual symbol
                        if sym in w or 'DIRECT HTTP' in w:
                            if not hasattr(self, '_working_tokens'):
                                self._working_tokens = {}
                            self._working_tokens[sym] = (w_exch, w_tok)
                            log_var.set(
                                f"✅ Auto-saved: {sym} → {w_exch}/{w_tok}. Try Fetch Data now!")
                            break
                else:
                    log_var.set(f"✅ API working (hardcoded tokens). Fetch Data should work now!")
            else:
                log_var.set("❌ Nothing worked. Share screenshot of debug window.")

        btn_row2 = tk.Frame(fetch_frame, bg='#f5f5f5')
        btn_row2.pack(pady=4)

        tk.Button(btn_row2, text="🔍 Lookup Token",
                  command=do_token_lookup,
                  bg='#7f8c8d', fg='white',
                  font=('Consolas', 9, 'bold'),
                  relief='flat', padx=10, pady=4,
                  cursor='hand2').pack(side='left', padx=3)

        tk.Button(btn_row2, text="🔬 Debug Test",
                  command=do_debug_test,
                  bg='#8e44ad', fg='white',
                  font=('Consolas', 9, 'bold'),
                  relief='flat', padx=10, pady=4,
                  cursor='hand2').pack(side='left', padx=3)

        def do_download_scrip():
            """Download Angel One scrip master — needed for options tokens."""
            import urllib.request, json as _j, ssl, os, gzip

            log_var.set("⏳ Downloading Angel One scrip master (~15MB)...")
            log_lbl.config(fg='#e67e22')
            win.update()

            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode    = ssl.CERT_NONE

            urls = [
                'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json',
                'https://angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json',
            ]

            for url in urls:
                try:
                    req  = urllib.request.Request(url, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                        'Accept':     'application/json, */*',
                    })
                    resp = urllib.request.urlopen(req, timeout=30, context=ctx)
                    raw  = resp.read()
                    try:
                        raw = gzip.decompress(raw)
                    except Exception:
                        pass
                    data = _j.loads(raw)

                    # Count NFO options
                    nfo_count = sum(1 for x in data
                                    if x.get('exch_seg') == 'NFO')

                    # Cache in memory
                    self._scrip_master = data

                    # Save to disk
                    cache = os.path.join(os.path.expanduser('~'),
                                         '.bulkowski_scrip.json')
                    with open(cache, 'w') as f:
                        _j.dump(data, f)

                    log_var.set(
                        f"✅ Scrip master downloaded! "
                        f"{len(data):,} instruments  |  "
                        f"NFO options: {nfo_count:,}  |  "
                        f"Saved to disk — options fetch will now work!")
                    log_lbl.config(fg='#27ae60')
                    messagebox.showinfo(
                        "Downloaded!",
                        f"✅ Angel One Scrip Master downloaded.\n\n"
                        f"Total instruments: {len(data):,}\n"
                        f"NFO options contracts: {nfo_count:,}\n\n"
                        f"You can now fetch any options symbol like:\n"
                        f"NIFTY25APR2424000CE\n"
                        f"BANKNIFTY25APR2448000CE\n\n"
                        f"File saved — won't need to download again.",
                        parent=win)
                    return
                except Exception as e:
                    continue

            log_var.set("❌ Download failed. Check internet connection.")
            log_lbl.config(fg='#e74c3c')
            messagebox.showerror(
                "Download Failed",
                "Could not download scrip master.\n\n"
                "Try manually:\n"
                "1. Open this URL in browser:\n"
                "   margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json\n"
                "2. Save as: C:\\Users\\pc\\.bulkowski_scrip.json\n"
                "3. Restart the app",
                parent=win)

        tk.Button(btn_row2, text="📋 Get Options Tokens",
                  command=do_download_scrip,
                  bg='#16a085', fg='white',
                  font=('Consolas', 9, 'bold'),
                  relief='flat', padx=10, pady=4,
                  cursor='hand2').pack(side='left', padx=3)

        # Show scrip master status
        import os
        cache_path = os.path.join(os.path.expanduser('~'), '.bulkowski_scrip.json')
        if os.path.exists(cache_path):
            size_mb = os.path.getsize(cache_path) / 1024 / 1024
            scrip_status = f"✅ Scrip master cached ({size_mb:.1f} MB) — options ready"
            scrip_col    = '#27ae60'
        else:
            scrip_status = "⚠ No scrip master — click 'Get Options Tokens' for options"
            scrip_col    = '#e67e22'

        tk.Label(fetch_frame, text=scrip_status,
                 bg='#f5f5f5', fg=scrip_col,
                 font=('Consolas', 7), anchor='w',
                 padx=4).pack(fill='x', pady=1)

        # Fetch button
        tk.Button(fetch_frame, text="📥  FETCH DATA",
                  command=do_fetch,
                  bg='#27ae60', fg='white',
                  font=('Consolas', 11, 'bold'),
                  relief='flat', padx=20, pady=8,
                  cursor='hand2').pack(pady=8)

        # ── PRESET SYMBOL REFERENCE ──────────────────────────────────────────
        ref_frame = tk.LabelFrame(win, text="  Common Symbols Reference  ",
                                   bg='#f5f5f5', fg=AO_DARK,
                                   font=('Consolas', 8, 'bold'),
                                   relief='groove', bd=1,
                                   padx=8, pady=4)
        ref_frame.pack(fill='x', padx=16, pady=4)

        ref_txt = ("Indices:  NIFTY 50 · BANKNIFTY · SENSEX · NIFTY IT · INDIA VIX\n"
                   "Stocks:   RELIANCE · TCS · HDFCBANK · INFY · ICICIBANK · SBIN · AXISBANK\n"
                   "Options:  NIFTY25APR2424000CE · NIFTY25APR2424000PE\n"
                   "          Format: SYMBOL + DDMMMYYYY + CE/PE + STRIKE  (Exchange: NFO)")
        tk.Label(ref_frame, text=ref_txt,
                 bg='#f5f5f5', fg='#666',
                 font=('Consolas', 7),
                 justify='left').pack(anchor='w')

    # ─────────────────────────────────────────────────────────────────────────
    #  LEVEL 1 — PATTERN COMPLETION FORECAST WINDOW
    # ─────────────────────────────────────────────────────────────────────────

    # ─────────────────────────────────────────────────────────────────────────
    #  BROOKS PA FORECAST WINDOW
    # ─────────────────────────────────────────────────────────────────────────

    def _show_brooks_forecast(self):
        """Brooks Price Action Forecast — Context-adjusted signal quality."""
        if self.df is None:
            messagebox.showwarning("No Data", "Load a CSV file first.")
            return
        if not getattr(self, 'brooks_signals', []):
            messagebox.showwarning("No Brooks Signals",
                "Click 🔍 Detect first to identify Brooks PA signals.")
            return

        BR_COL  = '#1a5c35'
        BR_LITE = '#1abc9c'

        win = tk.Toplevel(self.root)
        win.title("📐 Brooks PA Forecast — Signal Quality & Trade Plan")
        win.geometry('1150x1000')
        win.configure(bg='#f5f5f5')

        # ── Compute forecasts ─────────────────────────────────────────────
        forecasts = []
        for sig in self.brooks_signals:
            try:
                fc = compute_brooks_forecast(sig, self.df)
                forecasts.append(fc)
            except Exception as e:
                pass

        if not forecasts:
            messagebox.showinfo("No Forecast",
                "Could not compute forecasts. Run Detect first.")
            win.destroy()
            return

        # Context summary
        closes  = self.df['Close'].values
        n       = len(closes)
        ema200  = np.mean(closes[-min(200, n):])
        mkt     = 'BULL' if closes[-1] > ema200 else 'BEAR'
        try:
            adx_s, pdi_s, ndi_s = _adx(
                self.df['High'], self.df['Low'], self.df['Close'])
            adx_now = adx_s.iloc[-1]
            trend_str = 'STRONG' if adx_now > 30 else ('MODERATE' if adx_now > 20 else 'WEAK')
        except Exception:
            adx_now = 20; trend_str = 'MODERATE'

        # ── HEADER ───────────────────────────────────────────────────────
        hdr = tk.Frame(win, bg=BR_COL, pady=8, padx=16)
        hdr.pack(fill='x')
        tk.Label(hdr, text="📐  BROOKS PA — SIGNAL QUALITY FORECAST",
                 bg=BR_COL, fg='#e8f8f0',
                 font=('Consolas', 13, 'bold')).pack(side='left')
        tk.Label(hdr,
                 text=f"  |  {mkt} Market  |  "
                      f"ADX={adx_now:.1f} ({trend_str})  |  "
                      f"{len(forecasts)} signals",
                 bg=BR_COL, fg='#a9dfbf',
                 font=('Consolas', 9)).pack(side='left')

        # ── TOP: FORECAST CHART ─────────────────────────────────────────
        br_chart_outer = tk.Frame(win, bg='#f5f5f5')
        br_chart_outer.pack(fill='x', padx=8, pady=4)
        br_fig    = Figure(figsize=(11, 3.8), dpi=88)
        br_canvas = FigureCanvasTkAgg(br_fig, master=br_chart_outer)
        br_canvas.get_tk_widget().pack(fill='x')

        # ── BOTTOM: PANE ─────────────────────────────────────────────────
        pane = tk.PanedWindow(win, orient='horizontal',
                              bg='#d0d0d0', sashwidth=6)
        pane.pack(fill='both', expand=True, padx=8, pady=4)

        # Left: signal list
        left = tk.Frame(pane, bg='#f5f5f5')
        pane.add(left, width=300)

        tk.Label(left, text="DETECTED BROOKS SIGNALS",
                 bg='#f5f5f5', fg=BR_COL,
                 font=('Consolas', 10, 'bold'), pady=4).pack(fill='x')

        lb_fr = tk.Frame(left, bg='#f5f5f5')
        lb_fr.pack(fill='both', expand=True)
        lb_sb = tk.Scrollbar(lb_fr)
        lb    = tk.Listbox(lb_fr, bg='#ffffff', fg='#1a1d23',
                           selectbackground=BR_COL,
                           font=('Consolas', 9), relief='flat',
                           activestyle='none',
                           yscrollcommand=lb_sb.set)
        lb_sb.config(command=lb.yview)
        lb_sb.pack(side='right', fill='y')
        lb.pack(fill='both', expand=True)

        # Right: detail
        right = tk.Frame(pane, bg='#f5f5f5')
        pane.add(right)

        det = scrolledtext.ScrolledText(
            right, bg='#ffffff', fg='#1a1d23',
            font=('Consolas', 9), wrap=tk.WORD,
            relief='flat', padx=14, pady=10)
        det.pack(fill='both', expand=True)

        # Tags
        for tag, fg, font_w in [
            ('h1',    BR_COL,    'bold'),
            ('h2',    BR_LITE,   'bold'),
            ('bull',  '#27ae60', 'bold'),
            ('bear',  '#e74c3c', 'bold'),
            ('good',  '#2ecc71', 'bold'),
            ('warn',  '#e67e22', 'bold'),
            ('bad',   '#e74c3c', 'bold'),
            ('val',   '#1a1d23', 'normal'),
            ('lbl',   '#666666', 'normal'),
            ('div',   '#cccccc', 'normal'),
            ('rule',  '#5d6d7e', 'normal'),
            ('tgt',   '#1a5c35', 'bold'),
            ('risk',  '#c0392b', 'bold'),
            ('fp',    '#2980b9', 'normal'),
            ('grade', BR_COL,    'bold'),
        ]:
            size = 8 if tag in ('lbl', 'div', 'rule') else 9
            size = 12 if tag == 'h1' else size
            size = 10 if tag == 'h2' else size
            det.tag_config(tag, foreground=fg, font=('Consolas', size, font_w))

        def _bar(v, mx=100, w=35):
            f = int(v / mx * w)
            return '█' * f + '░' * (w - f)

        def show_fc(fc):
            det.config(state='normal')
            det.delete(1.0, tk.END)

            is_bull = '▲' in fc['signal'] or 'BULL' in fc['signal'].upper()
            d_tag   = 'bull' if is_bull else 'bear'

            # ── HEADER ─────────────────────────────────────────────────
            det.insert(tk.END, "\n📐  BROOKS PA SIGNAL FORECAST\n", 'h1')
            clean = fc['name'].replace('Brooks: ', '')
            det.insert(tk.END, f"    {clean.upper()}\n", 'h2')
            det.insert(tk.END, f"    Source: {fc['source']}\n\n", 'lbl')

            # Signal
            det.insert(tk.END, f"SIGNAL:  {fc['signal']}\n\n", d_tag)

            # ── SECTION 1: SIGNAL QUALITY SCORE ────────────────────────
            det.insert(tk.END, "─" * 52 + "\n", 'div')
            det.insert(tk.END, "\n🎯  SIGNAL QUALITY SCORE\n", 'h2')

            qs  = fc['quality_score']
            q_tag = 'good' if qs >= 75 else ('warn' if qs >= 55 else 'bad')
            det.insert(tk.END, f"  Overall Quality: ", 'lbl')
            det.insert(tk.END, f"{qs}/100\n", q_tag)
            det.insert(tk.END, f"  [{_bar(qs)}]\n\n", 'lbl')

            det.insert(tk.END,
                f"  Base score (signal type):     {fc['base_score']}\n", 'lbl')
            det.insert(tk.END,
                f"  Context adjustment:           "
                f"{'+'if fc['score_adj']>=0 else ''}{fc['score_adj']}\n", 'lbl')
            det.insert(tk.END,
                f"  Final quality score:          {qs}/100\n\n", q_tag)

            # ── SECTION 2: CONTEXT SCORING ──────────────────────────────
            det.insert(tk.END, "─" * 52 + "\n", 'div')
            det.insert(tk.END, "\n📊  CONTEXT FACTOR ANALYSIS\n", 'h2')
            det.insert(tk.END,
                "  (Brooks: Context is everything — the same setup is "
                "high or low probability\n"
                "   depending entirely on the surrounding price action)\n\n", 'fp')

            for icon, desc, pts in fc['context_items']:
                p_str = f"  ({'+' if pts > 0 else ''}{pts})" if pts != 0 else "  (  0)"
                c_tag = 'good' if pts > 0 else ('bad' if pts < 0 else 'lbl')
                det.insert(tk.END,
                    f"  {icon} {desc:<48}{p_str}\n", c_tag)

            always_in = fc['always_in']
            ai_tag = 'bull' if always_in == 'BULL' else \
                     ('bear' if always_in == 'BEAR' else 'lbl')
            det.insert(tk.END,
                f"\n  Always-in direction:  {always_in}\n", ai_tag)
            det.insert(tk.END,
                f"  ADX strength:         {fc['trend_strength']} "
                f"(ADX={fc['adx']:.1f})\n", 'lbl')
            det.insert(tk.END,
                f"  20 EMA:               {fc['ema20']:.2f}  "
                f"({'Above' if fc['curr'] > fc['ema20'] else 'Below'})\n", 'lbl')

            # ── SECTION 3: TRADE PLAN ───────────────────────────────────
            det.insert(tk.END, "\n" + "─" * 52 + "\n", 'div')
            det.insert(tk.END, "\n📋  EXACT TRADE PLAN\n", 'h2')

            det.insert(tk.END, "▸ ENTRY:\n", 'h2')
            det.insert(tk.END, f"  {fc['entry_txt']}\n\n", 'val')

            det.insert(tk.END, "▸ STOP LOSS:\n", 'h2')
            det.insert(tk.END, f"  {fc['stop_txt']}\n\n", 'risk')

            det.insert(tk.END, "▸ TARGETS:\n", 'h2')
            det.insert(tk.END, f"  {fc['target_txt']}\n\n", 'tgt')

            if fc['rr_val']:
                rr = fc['rr_val']
                rr_tag = 'good' if rr >= 2 else ('warn' if rr >= 1 else 'bad')
                grade  = 'A — Good' if rr >= 2 else ('B — Minimum' if rr >= 1 else 'D — Skip')
                det.insert(tk.END, f"  R:R Ratio: 1 : {rr:.1f}  Grade: {grade}\n\n", rr_tag)

            # ── SECTION 4: SCALE-OUT PLAN ───────────────────────────────
            det.insert(tk.END, "─" * 52 + "\n", 'div')
            det.insert(tk.END, "\n💰  SCALE-OUT PLAN (Brooks method)\n", 'h2')
            for line in fc['scale_plan']:
                det.insert(tk.END, f"  ◆ {line}\n", 'rule')

            # ── SECTION 5: POSITION SIZE ────────────────────────────────
            det.insert(tk.END, "\n" + "─" * 52 + "\n", 'div')
            det.insert(tk.END, "\n📏  POSITION SIZING\n", 'h2')
            det.insert(tk.END,
                f"  Trade Type:     {fc['trade_type'].upper()}\n", 'lbl')
            det.insert(tk.END,
                f"  Direction:      {'WITH TREND ✅' if fc['with_trend'] else ('COUNTER-TREND ⚠' if fc['counter_trend'] else 'NEUTRAL')}\n",
                'good' if fc['with_trend'] else ('warn' if fc['counter_trend'] else 'lbl'))
            det.insert(tk.END,
                f"  Size Rule:      {fc['size_rule']}\n\n", 'val')
            if fc['max_hold_bars'] > 0:
                det.insert(tk.END,
                    f"  ⏱ MAX HOLD:   {fc['max_hold_bars']} bars\n"
                    f"     If no reward by then — EXIT regardless.\n\n", 'warn')
            else:
                det.insert(tk.END,
                    f"  ⏱ HOLD RULE:  Trail indefinitely. "
                    f"Exit only when swing lows break.\n\n", 'rule')

            # ── SECTION 6: FAILURE SIGNALS ──────────────────────────────
            det.insert(tk.END, "─" * 52 + "\n", 'div')
            det.insert(tk.END,
                "\n⚠  EXIT IMMEDIATELY IF YOU SEE:\n", 'h2')
            det.insert(tk.END,
                "  (Brooks: The best traders exit fast when wrong)\n\n", 'fp')
            for i, f_sig in enumerate(fc['failure_signals'], 1):
                det.insert(tk.END, f"  {i}. {f_sig}\n", 'risk')

            # ── SECTION 7: BROOKS FIRST PRINCIPLE ──────────────────────
            if fc['db_entry']:
                det.insert(tk.END, "\n" + "─" * 52 + "\n", 'div')
                det.insert(tk.END,
                    "\n📖  WHY THIS SETUP WORKS (First Principle)\n", 'h2')
                det.insert(tk.END,
                    f"  {fc['db_entry']['first_principle']}\n\n", 'fp')
                det.insert(tk.END,
                    f"  Edge: {fc['db_entry']['edge']}\n", 'rule')

            # ── VERDICT ─────────────────────────────────────────────────
            det.insert(tk.END, "\n" + "─" * 52 + "\n", 'div')
            det.insert(tk.END, "\n📋  VERDICT\n", 'h2')
            v_tag = 'good' if '✅' in fc['verdict'] else \
                    ('warn' if '⚠' in fc['verdict'] else 'bad')
            det.insert(tk.END, f"  {fc['verdict']}\n", v_tag)
            det.insert(tk.END, f"  {fc['verdict_detail']}\n\n", 'rule')

            det.config(state='disabled')

        # Populate list
        for fc in forecasts:
            qs   = fc['quality_score']
            icon = '▲' if '▲' in fc['signal'] else ('▼' if '▼' in fc['signal'] else '◆')
            q_label = 'A+' if qs >= 80 else ('A' if qs >= 70 else ('B' if qs >= 55 else 'C'))
            lb.insert(tk.END,
                f" {icon} {fc['name'].replace('Brooks: ','')[:24]:<24} {qs}% [{q_label}]")

        def on_select(event):
            sel = lb.curselection()
            if not sel: return
            fc = forecasts[sel[0]]
            show_fc(fc)
            # Convert Brooks forecast to draw_forecast_chart format
            br_fc = {
                'is_bull':      '▲' in fc.get('signal','') or 'BULL' in fc.get('signal','').upper(),
                'neckline':     fc.get('entry_price'),
                'pattern_height': (abs(fc['entry_price'] - fc['stop_price'])
                                   if fc.get('entry_price') and fc.get('stop_price') else None),
                'target_1':     fc.get('t1'),
                'target_2':     fc.get('t2'),
                'target_3':     None,
                'completion_prob': fc.get('quality_score', 65),
                'throwback_prob':  None,
                'throwback_target': None,
                'est_completion_days': fc.get('max_hold_bars', 8),
                'performance_rank': fc.get('trade_type','').upper(),
                'pattern_name': fc.get('name','').replace('Brooks: ',''),
                'entry_price':  fc.get('entry_price'),
                'stop_price':   fc.get('stop_price'),
                't1': fc.get('t1'), 't2': fc.get('t2'),
                'quality_score': fc.get('quality_score', 65),
                'max_hold_bars': fc.get('max_hold_bars', 8),
                'trade_type':    fc.get('trade_type',''),
                'name':          fc.get('name',''),
                'signal':        fc.get('signal',''),
            }
            draw_forecast_chart(br_fig, self.df, br_fc, mode='brooks')
            br_canvas.draw()

        lb.bind('<<ListboxSelect>>', on_select)

        # Auto-select highest quality
        best_idx = max(range(len(forecasts)),
                       key=lambda i: forecasts[i]['quality_score'])
        lb.selection_set(best_idx)
        best_fc = forecasts[best_idx]
        show_fc(best_fc)
        br_fc_init = {
            'is_bull':      '▲' in best_fc.get('signal','') or 'BULL' in best_fc.get('signal','').upper(),
            'neckline':     best_fc.get('entry_price'),
            'pattern_height': (abs(best_fc['entry_price'] - best_fc['stop_price'])
                               if best_fc.get('entry_price') and best_fc.get('stop_price') else None),
            'target_1':     best_fc.get('t1'),
            'target_2':     best_fc.get('t2'),
            'target_3':     None,
            'completion_prob': best_fc.get('quality_score', 65),
            'throwback_prob': None, 'throwback_target': None,
            'est_completion_days': best_fc.get('max_hold_bars', 8),
            'performance_rank': best_fc.get('trade_type','').upper(),
            'pattern_name': best_fc.get('name','').replace('Brooks: ',''),
            'quality_score': best_fc.get('quality_score', 65),
            'max_hold_bars': best_fc.get('max_hold_bars', 8),
            'trade_type':    best_fc.get('trade_type',''),
            'name':          best_fc.get('name',''),
            'signal':        best_fc.get('signal',''),
        }
        draw_forecast_chart(br_fig, self.df, br_fc_init, mode='brooks')
        br_canvas.draw()

        # Bottom bar
        info = tk.Frame(win, bg=BR_COL, pady=5, padx=16)
        info.pack(fill='x')
        tk.Label(info,
                 text="📐 Context-adjusted quality score  "
                      "|  Based on Al Brooks' Trading Price Action Trends (Wiley, 2012)  "
                      "|  Always use stop losses",
                 bg=BR_COL, fg='#a9dfbf',
                 font=('Consolas', 8)).pack(side='left')

    # ─────────────────────────────────────────────────────────────────────────
    #  QUANT FORECAST WINDOW
    # ─────────────────────────────────────────────────────────────────────────

    def _show_quant_forecast(self):
        """Kakushadze Quant Signal Forecast — Aggregate consensus view."""
        if self.df is None:
            messagebox.showwarning("No Data", "Load a CSV file first.")
            return
        qsigs = getattr(self, 'quant_signals', [])
        if not qsigs:
            messagebox.showwarning("No Quant Signals",
                "Click 🔍 Detect first to compute quant signals.")
            return

        QC_COL  = '#2471a3'
        QC_LITE = '#5dade2'

        win = tk.Toplevel(self.root)
        win.title("📊 Quant Forecast — Kakushadze Signal Consensus")
        win.geometry('1150x1000')
        win.configure(bg='#f5f5f5')

        # ── Compute forecast ──────────────────────────────────────────────
        qfc = compute_quant_forecast(qsigs, self.df)
        if not qfc:
            messagebox.showinfo("Error", "Could not compute quant forecast.")
            win.destroy()
            return

        # ── HEADER ────────────────────────────────────────────────────────
        hdr = tk.Frame(win, bg=QC_COL, pady=8, padx=16)
        hdr.pack(fill='x')
        tk.Label(hdr, text="📊  QUANT SIGNAL FORECAST",
                 bg=QC_COL, fg='#ebf5fb',
                 font=('Consolas', 13, 'bold')).pack(side='left')
        tk.Label(hdr,
                 text=f"  |  {qfc['bull_count']}▲ Bull  "
                      f"{qfc['bear_count']}▼ Bear  "
                      f"{qfc['neut_count']}◆ Neutral  |  "
                      f"Agreement: {qfc['agreement_pct']}%  |  "
                      f"{qfc['total']} signals",
                 bg=QC_COL, fg='#aed6f1',
                 font=('Consolas', 9)).pack(side='left')

        # ── CHART ─────────────────────────────────────────────────────────
        chart_frame = tk.Frame(win, bg='#f5f5f5')
        chart_frame.pack(fill='x', padx=8, pady=4)
        qfc_fig    = Figure(figsize=(11, 3.8), dpi=88)
        qfc_canvas = FigureCanvasTkAgg(qfc_fig, master=chart_frame)
        qfc_canvas.get_tk_widget().pack(fill='x')
        draw_quant_forecast_chart(qfc_fig, self.df, qfc)
        qfc_canvas.draw()

        # ── CONTENT PANE ──────────────────────────────────────────────────
        pane = tk.PanedWindow(win, orient='horizontal',
                              bg='#d0d0d0', sashwidth=6)
        pane.pack(fill='both', expand=True, padx=8, pady=4)

        # Left: signal list
        left = tk.Frame(pane, bg='#f5f5f5')
        pane.add(left, width=320)

        tk.Label(left, text="ALL 16 QUANT SIGNALS",
                 bg='#f5f5f5', fg=QC_COL,
                 font=('Consolas', 10, 'bold'), pady=4).pack(fill='x')

        lb_fr = tk.Frame(left, bg='#f5f5f5')
        lb_fr.pack(fill='both', expand=True)
        lb_sb = tk.Scrollbar(lb_fr)
        lb    = tk.Listbox(lb_fr, bg='#ffffff', fg='#1a1d23',
                           selectbackground=QC_COL,
                           font=('Consolas', 8), relief='flat',
                           activestyle='none',
                           yscrollcommand=lb_sb.set)
        lb_sb.config(command=lb.yview)
        lb_sb.pack(side='right', fill='y')
        lb.pack(fill='both', expand=True)

        # Right: detail
        right = tk.Frame(pane, bg='#f5f5f5')
        pane.add(right)

        det = scrolledtext.ScrolledText(
            right, bg='#ffffff', fg='#1a1d23',
            font=('Consolas', 9), wrap=tk.WORD,
            relief='flat', padx=14, pady=10)
        det.pack(fill='both', expand=True)

        # Tags
        det.tag_config('h1',   foreground=QC_COL,    font=('Consolas', 12, 'bold'))
        det.tag_config('h2',   foreground=QC_LITE,   font=('Consolas', 10, 'bold'))
        det.tag_config('bull', foreground='#27ae60', font=('Consolas', 9, 'bold'))
        det.tag_config('bear', foreground='#e74c3c', font=('Consolas', 9, 'bold'))
        det.tag_config('neut', foreground='#888888', font=('Consolas', 9))
        det.tag_config('good', foreground='#2ecc71', font=('Consolas', 9, 'bold'))
        det.tag_config('warn', foreground='#e67e22', font=('Consolas', 9, 'bold'))
        det.tag_config('bad',  foreground='#e74c3c', font=('Consolas', 9, 'bold'))
        det.tag_config('val',  foreground='#1a1d23', font=('Consolas', 9))
        det.tag_config('lbl',  foreground='#666666', font=('Consolas', 8))
        det.tag_config('div',  foreground='#cccccc', font=('Consolas', 7))
        det.tag_config('tgt',  foreground='#1a5c35', font=('Consolas', 9, 'bold'))
        det.tag_config('rule', foreground='#5d6d7e', font=('Consolas', 8))
        det.tag_config('src',  foreground='#6d28d9', font=('Consolas', 8))

        def _bar(v, mx=100, w=35):
            f = int(v / mx * w)
            return '█' * f + '░' * (w - f)

        def show_aggregate():
            """Show the aggregate forecast summary."""
            det.config(state='normal')
            det.delete(1.0, tk.END)

            det.insert(tk.END, "\n📊  QUANT SIGNAL AGGREGATE FORECAST\n", 'h1')
            det.insert(tk.END,
                "    Kakushadze & Serur — 151 Trading Strategies (2018)\n\n", 'src')

            # ── Verdict ─────────────────────────────────────────────────
            v_tag = ('good' if '✅' in qfc['verdict'] else
                     'warn' if '⚠' in qfc['verdict'] else 'bad')
            det.insert(tk.END, f"VERDICT:  {qfc['verdict']}\n", v_tag)
            det.insert(tk.END, f"          {qfc['verdict_detail']}\n\n", 'rule')
            det.insert(tk.END, "─" * 52 + "\n", 'div')

            # ── Signal consensus ─────────────────────────────────────────
            det.insert(tk.END, "\n📈  SIGNAL CONSENSUS\n", 'h2')
            det.insert(tk.END,
                f"  Bullish signals:  {qfc['bull_count']:>2}  "
                f"[{'▲' * qfc['bull_count']}]\n", 'bull')
            det.insert(tk.END,
                f"  Bearish signals:  {qfc['bear_count']:>2}  "
                f"[{'▼' * qfc['bear_count']}]\n", 'bear')
            det.insert(tk.END,
                f"  Neutral signals:  {qfc['neut_count']:>2}  "
                f"[{'◆' * qfc['neut_count']}]\n\n", 'neut')

            agr = qfc['agreement_pct']
            a_tag = 'good' if agr >= 70 else ('warn' if agr >= 50 else 'bad')
            det.insert(tk.END,
                f"  Agreement Score:  {agr}%\n", a_tag)
            det.insert(tk.END,
                f"  [{_bar(agr)}]\n\n", 'lbl')

            det.insert(tk.END, "─" * 52 + "\n", 'div')

            # ── Price targets ─────────────────────────────────────────────
            det.insert(tk.END, "\n🎯  PRICE TARGET FORECAST\n", 'h2')
            curr    = qfc['curr']
            tgt1    = qfc['primary_tgt']
            tgt2    = qfc['secondary_tgt']
            mr      = qfc['mr_target']
            m1_pct  = (tgt1 - curr) / curr * 100
            m2_pct  = (tgt2 - curr) / curr * 100
            mr_pct  = (mr   - curr) / curr * 100
            is_bull = qfc['is_bull_bias']
            t_tag   = 'bull' if is_bull else 'bear'

            det.insert(tk.END, f"  Current Price:    {curr:>12,.2f}\n\n", 'val')
            det.insert(tk.END,
                f"  ▸ PRIMARY TARGET ({qfc['avg_horizon']} days):\n", 'h2')
            det.insert(tk.END,
                f"    {tgt1:>12,.2f}  "
                f"({'+' if m1_pct > 0 else ''}{m1_pct:.1f}%)\n", t_tag)
            det.insert(tk.END,
                f"    Based on {qfc['avg_move']:.1f}% avg move "
                f"from {qfc['bull_count'] if is_bull else qfc['bear_count']} "
                f"{'bullish' if is_bull else 'bearish'} signals\n\n", 'rule')

            det.insert(tk.END, f"  ▸ EXTENDED TARGET:\n", 'h2')
            det.insert(tk.END,
                f"    {tgt2:>12,.2f}  "
                f"({'+' if m2_pct > 0 else ''}{m2_pct:.1f}%)\n\n", t_tag)

            det.insert(tk.END, f"  ▸ MEAN REVERSION TARGET (if reversal):\n", 'h2')
            det.insert(tk.END,
                f"    {mr:>12,.2f}  "
                f"({'+' if mr_pct > 0 else ''}{mr_pct:.1f}%)  "
                f"← 20-day average\n\n", 'warn')

            det.insert(tk.END, "─" * 52 + "\n", 'div')

            # ── Pivot levels ──────────────────────────────────────────────
            if qfc.get('pivot'):
                det.insert(tk.END, "\n📐  PIVOT LEVELS (FROM QUANT SIGNAL)\n", 'h2')
                det.insert(tk.END,
                    f"  R2 (2nd Resistance):  "
                    f"{qfc['r2']:>10,.2f}\n" if qfc.get('r2') else "", 'bear')
                det.insert(tk.END,
                    f"  R1 (1st Resistance):  "
                    f"{qfc['r1']:>10,.2f}\n" if qfc.get('r1') else "", 'bear')
                det.insert(tk.END,
                    f"  Pivot Point:          "
                    f"{qfc['pivot']:>10,.2f}  ← key daily level\n", 'lbl')
                det.insert(tk.END,
                    f"  S1 (1st Support):     "
                    f"{qfc['s1']:>10,.2f}\n" if qfc.get('s1') else "", 'bull')
                det.insert(tk.END,
                    f"  S2 (2nd Support):     "
                    f"{qfc['s2']:>10,.2f}\n\n" if qfc.get('s2') else "", 'bull')

            det.insert(tk.END, "─" * 52 + "\n", 'div')

            # ── Z-score / mean reversion ──────────────────────────────────
            if qfc.get('zscore_val') is not None:
                z = qfc['zscore_val']
                z_tag = ('bull' if z < -1.5 else
                         'bear' if z > 1.5 else 'lbl')
                det.insert(tk.END, "\n📉  MEAN REVERSION STATUS\n", 'h2')
                det.insert(tk.END,
                    f"  Current Z-Score:  {z:+.2f}\n", z_tag)
                if z <= -2:
                    det.insert(tk.END,
                        "  Status: DEEPLY OVERSOLD → strong mean reversion buy\n", 'bull')
                elif z <= -1.5:
                    det.insert(tk.END,
                        "  Status: Oversold → mean reversion buy setup\n", 'bull')
                elif z >= 2:
                    det.insert(tk.END,
                        "  Status: DEEPLY OVERBOUGHT → strong mean reversion sell\n", 'bear')
                elif z >= 1.5:
                    det.insert(tk.END,
                        "  Status: Overbought → mean reversion sell setup\n", 'bear')
                else:
                    det.insert(tk.END,
                        "  Status: Within normal range — no mean reversion signal\n", 'lbl')
                det.insert(tk.END, "\n")

            det.insert(tk.END, "─" * 52 + "\n", 'div')

            # ── Position sizing ───────────────────────────────────────────
            det.insert(tk.END, "\n💼  POSITION SIZING\n", 'h2')
            s_tag = ('good'  if 'FULL' in qfc['size_advice'] else
                     'warn'  if 'REDUCE' in qfc['size_advice'] else 'lbl')
            det.insert(tk.END,
                f"  Vol-Weighted Score:  "
                f"{qfc['vw_score']:+.3f}\n" if qfc.get('vw_score') else
                "  Vol-Weighted Score:  N/A\n", 'lbl')
            det.insert(tk.END,
                f"  Recommendation:     {qfc['size_advice']}\n\n", s_tag)

            det.insert(tk.END, "─" * 52 + "\n", 'div')

            # ── Signal contribution table ─────────────────────────────────
            det.insert(tk.END, "\n📋  ALL SIGNAL CONTRIBUTIONS\n", 'h2')
            det.insert(tk.END,
                f"  {'Signal':<28} {'Dir':<8} {'Str':>4}  "
                f"{'Horizon':>7}  {'E.Move':>6}\n", 'lbl')
            det.insert(tk.END, "  " + "─" * 60 + "\n", 'div')

            for c in qfc['contributions']:
                d_tag = ('bull' if '▲' in c['direction'] else
                         'bear' if '▼' in c['direction'] else 'neut')
                det.insert(tk.END,
                    f"  {c['name']:<28} {c['direction'][:7]:<8} "
                    f"{c['strength']:>3.0f}%  "
                    f"{c['horizon']:>5}d  "
                    f"{c['exp_move']:>5.1f}%\n", d_tag)

            det.config(state='disabled')

        def show_signal_detail(sig):
            """Show detail for a single selected quant signal."""
            det.config(state='normal')
            det.delete(1.0, tk.END)
            is_bull = sig['color'] == '#2ecc71'
            d_tag   = 'bull' if is_bull else ('bear' if sig['color'] == '#e74c3c' else 'neut')

            det.insert(tk.END, f"\n{sig['name'].upper()}\n", 'h1')
            det.insert(tk.END, f"Source: {sig['source']}\n\n", 'src')

            det.insert(tk.END, f"SIGNAL:    {sig['icon']} {sig['signal']}\n", d_tag)
            st = sig.get('strength', 50)
            det.insert(tk.END,
                f"STRENGTH:  {st:.0f}%  [{_bar(st, w=30)}]\n\n", 'lbl')
            det.insert(tk.END, f"VALUE:\n  {sig['value']}\n\n", 'val')

            det.insert(tk.END, "─── EXPLANATION ─────────────────────────\n", 'div')
            det.insert(tk.END, f"{sig['desc']}\n\n", 'rule')
            det.insert(tk.END, "─── TRADING RULES ───────────────────────\n", 'div')
            for line in sig['trade_rule'].split('\n'):
                det.insert(tk.END, f"  {line}\n", 'rule')

            det.config(state='disabled')

        # Populate list — summary line first, then each signal
        lb.insert(tk.END, " 📊 ── AGGREGATE FORECAST ──────────────")
        for c in qfc['contributions']:
            icon = '▲' if '▲' in c['direction'] else \
                   ('▼' if '▼' in c['direction'] else '◆')
            lb.insert(tk.END,
                f" {icon} {c['name']:<28} {c['strength']:>3.0f}%")

        def on_select(event):
            sel = lb.curselection()
            if not sel: return
            idx = sel[0]
            if idx == 0:
                show_aggregate()
            else:
                # Map to actual quant signal
                sig_idx = idx - 1
                if sig_idx < len(qsigs):
                    # Find matching signal by name
                    contrib_name = qfc['contributions'][sig_idx]['name']
                    for sig in qsigs:
                        if sig['name'][:28] == contrib_name:
                            show_signal_detail(sig)
                            break

        lb.bind('<<ListboxSelect>>', on_select)

        # Auto-show aggregate
        lb.selection_set(0)
        show_aggregate()

        # Bottom bar
        info = tk.Frame(win, bg=QC_COL, pady=5, padx=16)
        info.pack(fill='x')
        tk.Label(info,
                 text="📊 Kakushadze & Serur — 151 Trading Strategies (2018)  "
                      "|  Click any signal for detail  "
                      "|  Click top row for aggregate forecast",
                 bg=QC_COL, fg='#aed6f1',
                 font=('Consolas', 8)).pack(side='left')

    def _show_forecast(self):
        """Pattern Completion Forecasting — Level 1 Prediction Engine."""
        if self.df is None:
            messagebox.showwarning("No Data", "Load a CSV file first.", )
            return
        if not self.detected:
            messagebox.showwarning("No Patterns",
                "Click 🔍 Detect first to identify patterns.")
            return

        FC_COL  = '#9b59b6'
        FC_DARK = '#6c3483'

        win = tk.Toplevel(self.root)
        win.title("🔮 Pattern Completion Forecast — Level 1 Prediction")
        win.geometry('1150x1000')
        win.configure(bg='#f5f5f5')

        # ── Detect market context (bull/bear from 200-day MA) ─────────────
        closes = self.df['Close'].values
        n      = len(closes)
        ma200  = np.mean(closes[-min(200, n):])
        mkt    = 'bull' if closes[-1] > ma200 else 'bear'
        mkt_lbl = f"{'📈 BULL' if mkt=='bull' else '📉 BEAR'} MARKET  " \
                  f"(Price {closes[-1]:.2f} {'above' if mkt=='bull' else 'below'} " \
                  f"200-day MA {ma200:.2f})"

        # ── Compute forecasts for all detected patterns ───────────────────
        forecasts = []
        for pat in self.detected:
            try:
                fc = compute_pattern_forecast(pat, self.df, mkt)
                forecasts.append(fc)
            except Exception:
                pass

        if not forecasts:
            messagebox.showinfo("No Forecast",
                "Could not compute forecasts. Run Detect first.")
            win.destroy()
            return

        # ── HEADER ───────────────────────────────────────────────────────
        hdr = tk.Frame(win, bg=FC_DARK, pady=8, padx=16)
        hdr.pack(fill='x')
        tk.Label(hdr, text="🔮  PATTERN COMPLETION FORECAST",
                 bg=FC_DARK, fg='#f0e6ff',
                 font=('Consolas', 13, 'bold')).pack(side='left')
        tk.Label(hdr, text=f"  |  {mkt_lbl}",
                 bg=FC_DARK, fg='#c39bd3',
                 font=('Consolas', 9)).pack(side='left')
        tk.Label(hdr,
                 text=f"{len(forecasts)} pattern(s) analysed",
                 bg=FC_DARK, fg='#a569bd',
                 font=('Consolas', 9)).pack(side='right')

        # ── TOP: FORECAST CHART ──────────────────────────────────────────
        chart_outer = tk.Frame(win, bg='#f5f5f5', relief='flat', bd=1)
        chart_outer.pack(fill='x', padx=8, pady=4)

        fc_fig = Figure(figsize=(11, 3.8), dpi=88)
        fc_canvas = FigureCanvasTkAgg(fc_fig, master=chart_outer)
        fc_canvas.get_tk_widget().pack(fill='x')

        # ── BOTTOM: MAIN PANE ─────────────────────────────────────────────
        pane = tk.PanedWindow(win, orient='horizontal',
                              bg='#e0e0e0', sashwidth=6)
        pane.pack(fill='both', expand=True, padx=8, pady=4)

        # Left: pattern list
        left = tk.Frame(pane, bg='#f5f5f5')
        pane.add(left, width=310)

        tk.Label(left, text="DETECTED PATTERNS",
                 bg='#f5f5f5', fg=FC_DARK,
                 font=('Consolas', 10, 'bold'), pady=4).pack(fill='x')

        lb_fr = tk.Frame(left, bg='#f5f5f5')
        lb_fr.pack(fill='both', expand=True)
        lb_sb = tk.Scrollbar(lb_fr)
        lb    = tk.Listbox(lb_fr, bg='#ffffff', fg='#1a1d23',
                           selectbackground=FC_COL,
                           font=('Consolas', 9), relief='flat',
                           activestyle='none',
                           yscrollcommand=lb_sb.set)
        lb_sb.config(command=lb.yview)
        lb_sb.pack(side='right', fill='y')
        lb.pack(fill='both', expand=True)

        # Right: forecast detail
        right = tk.Frame(pane, bg='#f5f5f5')
        pane.add(right)

        det = scrolledtext.ScrolledText(
            right, bg='#ffffff', fg='#1a1d23',
            font=('Consolas', 9), wrap=tk.WORD,
            relief='flat', padx=14, pady=10)
        det.pack(fill='both', expand=True)

        # Tags
        det.tag_config('h1',    foreground=FC_DARK,   font=('Consolas', 12, 'bold'))
        det.tag_config('h2',    foreground=FC_COL,    font=('Consolas', 10, 'bold'))
        det.tag_config('bull',  foreground='#27ae60', font=('Consolas', 9, 'bold'))
        det.tag_config('bear',  foreground='#e74c3c', font=('Consolas', 9, 'bold'))
        det.tag_config('gold',  foreground='#d4ac0d', font=('Consolas', 9, 'bold'))
        det.tag_config('val',   foreground='#1a1d23', font=('Consolas', 9))
        det.tag_config('lbl',   foreground='#666',    font=('Consolas', 8))
        det.tag_config('div',   foreground='#cccccc', font=('Consolas', 7))
        det.tag_config('good',  foreground='#2ecc71', font=('Consolas', 9, 'bold'))
        det.tag_config('warn',  foreground='#e67e22', font=('Consolas', 9, 'bold'))
        det.tag_config('bad',   foreground='#e74c3c', font=('Consolas', 9, 'bold'))
        det.tag_config('prob',  foreground='#2980b9', font=('Consolas', 11, 'bold'))
        det.tag_config('tgt',   foreground='#1a7a4a', font=('Consolas', 9, 'bold'))
        det.tag_config('risk',  foreground='#c0392b', font=('Consolas', 9, 'bold'))
        det.tag_config('rule',  foreground='#5d6d7e', font=('Consolas', 8))
        det.tag_config('grade_a',foreground='#2ecc71',font=('Consolas', 11, 'bold'))
        det.tag_config('grade_b',foreground='#f1c40f',font=('Consolas', 11, 'bold'))
        det.tag_config('grade_c',foreground='#e74c3c',font=('Consolas', 11, 'bold'))

        def _bar(value, max_val=100, width=30, fill='█', empty='░'):
            filled = int(value / max_val * width)
            return fill * filled + empty * (width - filled)

        def show_forecast(fc):
            det.config(state='normal')
            det.delete(1.0, tk.END)

            is_bull = fc['is_bull']
            dir_tag = 'bull' if is_bull else 'bear'
            dir_sym = '▲' if is_bull else '▼'

            # ── HEADER ───────────────────────────────────────────────────
            det.insert(tk.END, f"\n🔮  PATTERN FORECAST\n", 'h1')
            det.insert(tk.END, f"    {fc['pattern_name'].upper()}\n\n", 'h2')

            # Conviction Grade (big, prominent)
            g = fc['conviction_grade']
            g_tag = 'grade_a' if g.startswith('A') else \
                    ('grade_b' if g.startswith('B') or g.startswith('C') else 'grade_c')
            det.insert(tk.END, f"CONVICTION GRADE:  {g}\n", g_tag)
            det.insert(tk.END,
                f"Score: {fc['conviction_score']}/100   "
                f"[{_bar(fc['conviction_score'])}]\n\n", 'lbl')

            det.insert(tk.END, "─" * 52 + "\n", 'div')

            # ── SECTION 1: COMPLETION PROBABILITY ────────────────────────
            det.insert(tk.END, "\n📊  COMPLETION PROBABILITY\n", 'h2')

            prob  = fc['completion_prob']
            p_tag = 'good' if prob >= 70 else ('warn' if prob >= 50 else 'bad')
            det.insert(tk.END,
                f"  Probability this pattern completes: ", 'lbl')
            det.insert(tk.END, f"{prob}%\n", p_tag)
            det.insert(tk.END,
                f"  [{_bar(prob, width=40)}]\n\n", 'lbl')

            det.insert(tk.END,
                f"  Breakeven Failure Rate:  ", 'lbl')
            f_tag = 'good' if fc['failure_rate'] < 10 else ('warn' if fc['failure_rate'] < 20 else 'bad')
            det.insert(tk.END,
                f"{fc['failure_rate']:.0f}%  "
                f"({'Low risk' if fc['failure_rate'] < 10 else ('Moderate' if fc['failure_rate'] < 20 else 'High risk')})\n", f_tag)
            det.insert(tk.END,
                f"  Bulkowski Sample Size:    {fc['samples']:,} patterns\n", 'lbl')
            det.insert(tk.END,
                f"  Performance Rank:         {fc['performance_rank']}\n", 'lbl')
            det.insert(tk.END,
                f"  Market Context:           {fc['market_context'].upper()} market\n\n", 'lbl')

            det.insert(tk.END, "─" * 52 + "\n", 'div')

            # ── SECTION 2: PRICE TARGETS ──────────────────────────────────
            det.insert(tk.END, "\n🎯  PRICE TARGET FORECAST\n", 'h2')
            det.insert(tk.END,
                f"  Current Price:    {fc['current_price']:>10.2f}\n", 'val')
            if fc['neckline']:
                det.insert(tk.END,
                    f"  Neckline/Entry:   {fc['neckline']:>10.2f}\n", 'val')
            det.insert(tk.END,
                f"  Pattern Height:   {fc['pattern_height']:>10.2f} pts\n\n", 'val')

            # Target 1
            t1_tag = 'bull' if is_bull else 'bear'
            det.insert(tk.END, f"  ▸ TARGET 1 (Measure Rule — {fc['target_reliability']:.0f}% reliable):\n", 'h2')
            det.insert(tk.END,
                f"    {fc['target_1']:>10.2f}  "
                f"({'+' if fc['move_to_t1_pct'] > 0 else ''}{fc['move_to_t1_pct']:.1f}% from current)\n", t1_tag)
            if fc['measure_rule']:
                det.insert(tk.END,
                    f"    Rule: {fc['measure_rule'][:80]}\n", 'rule')

            det.insert(tk.END, f"\n  ▸ TARGET 2 (Extended — 150% of height):\n", 'h2')
            det.insert(tk.END,
                f"    {fc['target_2']:>10.2f}  "
                f"({'+' if fc['move_to_t2_pct'] > 0 else ''}{fc['move_to_t2_pct']:.1f}% from current)\n", t1_tag)

            det.insert(tk.END, f"\n  ▸ TARGET 3 (Maximum — 200% of height):\n", 'h2')
            det.insert(tk.END,
                f"    {fc['target_3']:>10.2f}  "
                f"({'Major resistance zone if reached'})\n\n", t1_tag)

            det.insert(tk.END, "─" * 52 + "\n", 'div')

            # ── SECTION 3: TIME FORECAST ──────────────────────────────────
            det.insert(tk.END, "\n⏱  TIME TO COMPLETION FORECAST\n", 'h2')
            det.insert(tk.END,
                f"  Estimated trading days to complete:  "
                f"~{fc['est_completion_days']} days\n", 'val')
            det.insert(tk.END,
                f"  Estimated calendar weeks:            "
                f"~{fc['est_completion_days'] // 5 + 1} weeks\n\n", 'val')

            det.insert(tk.END, "─" * 52 + "\n", 'div')

            # ── SECTION 4: THROWBACK/PULLBACK FORECAST ───────────────────
            tb_word = "Throwback" if is_bull else "Pullback"
            det.insert(tk.END, f"\n↩  {tb_word.upper()} PROBABILITY\n", 'h2')
            tb_tag = 'warn' if fc['throwback_prob'] > 50 else 'good'
            det.insert(tk.END,
                f"  Probability of {tb_word.lower()} to neckline: ", 'lbl')
            det.insert(tk.END, f"{fc['throwback_prob']}%\n", tb_tag)
            det.insert(tk.END,
                f"  [{_bar(fc['throwback_prob'], width=40)}]\n\n", 'lbl')
            det.insert(tk.END,
                f"  {tb_word} target level:   {fc['throwback_target']:.2f}\n", 'val')
            det.insert(tk.END,
                f"  Typical timing:           within {fc['throwback_days']} days\n\n", 'val')
            det.insert(tk.END, "  WHAT TO DO IF THROWBACK OCCURS:\n", 'h2')
            for line in fc['throwback_action'].split('\n'):
                det.insert(tk.END, f"  {line}\n", 'rule')

            det.insert(tk.END, "\n" + "─" * 52 + "\n", 'div')

            # ── SECTION 5: FAILURE SCENARIOS ─────────────────────────────
            det.insert(tk.END, "\n⚠  FAILURE SCENARIOS — EXIT IF:\n", 'h2')
            for i, scenario in enumerate(fc['failure_scenarios'], 1):
                det.insert(tk.END, f"  {i}. {scenario}\n", 'risk')

            det.insert(tk.END, "\n" + "─" * 52 + "\n", 'div')

            # ── SECTION 6: BEST CONDITIONS ────────────────────────────────
            det.insert(tk.END, "\n✅  BEST CONDITIONS FOR THIS PATTERN\n", 'h2')
            det.insert(tk.END,
                "  (Check how many apply to the current setup)\n\n", 'lbl')
            for cond in fc['best_conditions']:
                det.insert(tk.END, f"  ◆ {cond}\n", 'rule')

            det.insert(tk.END, "\n" + "─" * 52 + "\n", 'div')

            # ── SECTION 7: TRADING DECISION SUMMARY ──────────────────────
            det.insert(tk.END, "\n📋  TRADING DECISION SUMMARY\n", 'h2')

            # Should you trade?
            if fc['conviction_score'] >= 75 and prob >= 65:
                det.insert(tk.END,
                    "  VERDICT: ✅ HIGH PROBABILITY SETUP — WORTH TRADING\n", 'good')
                det.insert(tk.END,
                    f"  Reason: {prob}% completion probability + strong "
                    f"Bulkowski statistics ({fc['samples']:,} samples)\n\n", 'rule')
            elif fc['conviction_score'] >= 55 and prob >= 50:
                det.insert(tk.END,
                    "  VERDICT: ⚠ MODERATE SETUP — TRADE WITH REDUCED SIZE\n", 'warn')
                det.insert(tk.END,
                    f"  Reason: {prob}% completion probability — use 50% normal position size\n\n", 'rule')
            else:
                det.insert(tk.END,
                    "  VERDICT: ❌ LOW PROBABILITY — SKIP OR PAPER TRADE ONLY\n", 'bad')
                det.insert(tk.END,
                    f"  Reason: Only {prob}% completion probability. "
                    f"Wait for a better setup.\n\n", 'rule')

            # Action plan
            det.insert(tk.END, "  ACTION PLAN:\n", 'h2')
            if fc['neckline']:
                entry_cond = (f"Close above {fc['neckline']:.2f}"
                              if is_bull else
                              f"Close below {fc['neckline']:.2f}")
                det.insert(tk.END,
                    f"  1. Wait for: {entry_cond} (neckline break)\n", 'val')
            det.insert(tk.END,
                f"  2. Target 1: {fc['target_1']:.2f} "
                f"({'+' if fc['move_to_t1_pct'] > 0 else ''}{fc['move_to_t1_pct']:.1f}%) "
                f"— scale 50% here\n", 'tgt')
            det.insert(tk.END,
                f"  3. Target 2: {fc['target_2']:.2f} "
                f"({'+' if fc['move_to_t2_pct'] > 0 else ''}{fc['move_to_t2_pct']:.1f}%) "
                f"— scale 30% here\n", 'tgt')
            det.insert(tk.END,
                f"  4. Runner:   {fc['target_3']:.2f} — hold 20% with trailing stop\n", 'tgt')
            det.insert(tk.END,
                f"  5. Time out: If target not reached in {fc['est_completion_days']} days — exit\n", 'warn')
            det.insert(tk.END, "\n")

            det.config(state='disabled')

        # Populate listbox
        for fc in forecasts:
            icon = '▲' if fc['is_bull'] else '▼'
            grade = fc['conviction_grade'][:2].strip()
            prob  = fc['completion_prob']
            lb.insert(tk.END,
                f" {icon} {fc['pattern_name'][:24]:<24}  {prob}%  [{grade}]")

        def on_select(event):
            sel = lb.curselection()
            if not sel: return
            fc = forecasts[sel[0]]
            show_forecast(fc)
            # Redraw forecast chart
            draw_forecast_chart(fc_fig, self.df, fc, mode='bulkowski')
            fc_canvas.draw()

        lb.bind('<<ListboxSelect>>', on_select)

        # Auto-select best (highest conviction score)
        best_idx = max(range(len(forecasts)),
                       key=lambda i: forecasts[i]['conviction_score'])
        lb.selection_set(best_idx)
        best_fc = forecasts[best_idx]
        show_forecast(best_fc)
        draw_forecast_chart(fc_fig, self.df, best_fc, mode='bulkowski')
        fc_canvas.draw()

        # Bottom bar
        info = tk.Frame(win, bg='#6c3483', pady=5, padx=16)
        info.pack(fill='x')
        tk.Label(info,
                 text="🔮 Based on Bulkowski's 38,500-sample database  "
                      "|  Probabilities are historical averages — not guarantees  "
                      "|  Always use stop losses",
                 bg='#6c3483', fg='#d7bde2',
                 font=('Consolas', 8)).pack(side='left')

    # ─────────────────────────────────────────────────────────────────────────
    #  BACKTESTING ENGINE WINDOW
    # ─────────────────────────────────────────────────────────────────────────

    def _show_backtest(self):
        """Backtesting Engine — test patterns on historical data."""
        if self.df is None:
            messagebox.showwarning("No Data",
                "Load a CSV file first.\n\n"
                "For best results: load 1–2 years of daily OHLC data.\n"
                "The more history, the more reliable the backtest.")
            return

        n = len(self.df)
        if n < 100:
            messagebox.showwarning("Insufficient Data",
                f"Backtest needs at least 100 bars. You have {n}.\n\n"
                "Load more historical data (1–2 years recommended).")
            return

        BT_COL  = '#922b21'
        BT_LITE = '#e74c3c'

        win = tk.Toplevel(self.root)
        win.title("📉 Backtest Engine — Pattern Historical Performance")
        win.geometry('1150x900')
        win.configure(bg='#f5f5f5')
        win.resizable(True, True)

        # ── HEADER ────────────────────────────────────────────────────────
        hdr = tk.Frame(win, bg=BT_COL, pady=8, padx=16)
        hdr.pack(fill='x')
        tk.Label(hdr, text="📉  BACKTEST ENGINE",
                 bg=BT_COL, fg='#fdf2f2',
                 font=('Consolas', 13, 'bold')).pack(side='left')
        tk.Label(hdr,
                 text=f"  |  {n} bars available  |  "
                      f"{str(self.df['Date'].iloc[0])[:10]} → "
                      f"{str(self.df['Date'].iloc[-1])[:10]}",
                 bg=BT_COL, fg='#f1948a',
                 font=('Consolas', 9)).pack(side='left')

        # ── SETTINGS PANEL ────────────────────────────────────────────────
        settings = tk.LabelFrame(win, text="  Backtest Settings  ",
                                  bg='#f5f5f5', fg=BT_COL,
                                  font=('Consolas', 9, 'bold'),
                                  relief='groove', bd=2,
                                  padx=16, pady=10)
        settings.pack(fill='x', padx=10, pady=8)

        row1 = tk.Frame(settings, bg='#f5f5f5')
        row1.pack(fill='x', pady=3)

        # Pattern type selector
        tk.Label(row1, text="Pattern Type:", bg='#f5f5f5', fg='#333',
                 font=('Consolas', 9), width=16, anchor='w').pack(side='left')

        pattern_choices = [
            'Double Bottom', 'Double Top',
            'Head-and-Shoulders Bottom', 'Head-and-Shoulders Top',
            'Triple Bottom', 'Triple Top',
            'Ascending Triangle', 'Descending Triangle',
            'Symmetrical Triangle', 'Cup with Handle',
            'Bull Flag', 'Measured Move Up',
        ]
        pat_var = tk.StringVar(value='Double Bottom')
        pat_menu = ttk.Combobox(row1, textvariable=pat_var,
                                values=pattern_choices,
                                width=28, state='readonly',
                                font=('Consolas', 9))
        pat_menu.pack(side='left', padx=6)

        # Direction (auto-set based on pattern)
        tk.Label(row1, text="Direction:", bg='#f5f5f5', fg='#333',
                 font=('Consolas', 9), width=10, anchor='w').pack(side='left')
        dir_var = tk.StringVar(value='BULLISH')
        dir_menu = ttk.Combobox(row1, textvariable=dir_var,
                                values=['BULLISH', 'BEARISH'],
                                width=10, state='readonly',
                                font=('Consolas', 9))
        dir_menu.pack(side='left', padx=4)

        # Auto-set direction based on pattern
        def on_pattern_change(event=None):
            p = pat_var.get()
            if any(x in p for x in ['Bottom', 'Bull', 'Ascending', 'Cup', 'Measured']):
                dir_var.set('BULLISH')
            else:
                dir_var.set('BEARISH')
        pat_menu.bind('<<ComboboxSelected>>', on_pattern_change)

        row2 = tk.Frame(settings, bg='#f5f5f5')
        row2.pack(fill='x', pady=3)

        tk.Label(row2, text="Min Confidence:", bg='#f5f5f5', fg='#333',
                 font=('Consolas', 9), width=16, anchor='w').pack(side='left')
        conf_var = tk.IntVar(value=60)
        tk.Scale(row2, variable=conf_var, from_=40, to=90,
                 orient='horizontal', length=200,
                 bg='#f5f5f5', fg='#333',
                 troughcolor='#e0e0e0',
                 font=('Consolas', 8)).pack(side='left')
        conf_lbl = tk.Label(row2, textvariable=tk.StringVar(),
                            bg='#f5f5f5', fg='#333',
                            font=('Consolas', 9))
        conf_lbl.pack(side='left', padx=4)

        def update_conf_lbl(*args):
            conf_lbl.config(text=f"{conf_var.get()}%")
        conf_var.trace('w', update_conf_lbl)
        update_conf_lbl()

        tk.Label(row2, text="Max Hold (bars):", bg='#f5f5f5', fg='#333',
                 font=('Consolas', 9), width=16, anchor='w').pack(side='left', padx=(20,0))
        hold_var = tk.IntVar(value=30)
        tk.Scale(row2, variable=hold_var, from_=10, to=60,
                 orient='horizontal', length=150,
                 bg='#f5f5f5', fg='#333',
                 troughcolor='#e0e0e0',
                 font=('Consolas', 8)).pack(side='left')

        # Progress bar
        progress_var = tk.DoubleVar(value=0)
        prog_bar = ttk.Progressbar(settings, variable=progress_var,
                                    maximum=100, length=400,
                                    mode='determinate')
        prog_bar.pack(pady=6)

        status_var = tk.StringVar(value="Configure settings and click Run Backtest.")
        tk.Label(settings, textvariable=status_var,
                 bg='#f5f5f5', fg='#666',
                 font=('Consolas', 8)).pack()

        # ── RESULTS AREA ─────────────────────────────────────────────────
        results_pane = tk.PanedWindow(win, orient='horizontal',
                                       bg='#d0d0d0', sashwidth=6)
        results_pane.pack(fill='both', expand=True, padx=10, pady=4)

        # Left: trade list
        left = tk.Frame(results_pane, bg='#f5f5f5')
        results_pane.add(left, width=380)

        tk.Label(left, text="TRADE-BY-TRADE RESULTS",
                 bg='#f5f5f5', fg=BT_COL,
                 font=('Consolas', 10, 'bold'), pady=4).pack(fill='x')

        lb_fr = tk.Frame(left, bg='#f5f5f5')
        lb_fr.pack(fill='both', expand=True)
        lb_sb = tk.Scrollbar(lb_fr)
        lb    = tk.Listbox(lb_fr, bg='#ffffff', fg='#1a1d23',
                           selectbackground=BT_COL,
                           font=('Consolas', 8), relief='flat',
                           activestyle='none',
                           yscrollcommand=lb_sb.set)
        lb_sb.config(command=lb.yview)
        lb_sb.pack(side='right', fill='y')
        lb.pack(fill='both', expand=True)

        # Right: stats + equity
        right = tk.Frame(results_pane, bg='#f5f5f5')
        results_pane.add(right)

        # Stats text
        stats_text = scrolledtext.ScrolledText(
            right, bg='#ffffff', fg='#1a1d23',
            font=('Consolas', 9), wrap=tk.WORD,
            relief='flat', padx=12, pady=10,
            height=14)
        stats_text.pack(fill='x')

        # Equity curve chart
        eq_fig    = Figure(figsize=(7, 3.2), dpi=88)
        eq_canvas = FigureCanvasTkAgg(eq_fig, master=right)
        eq_canvas.get_tk_widget().pack(fill='both', expand=True, pady=4)

        # Tags
        for tag, fg, fw in [
            ('h1',   BT_COL,    'bold'),
            ('h2',   BT_LITE,   'bold'),
            ('win',  '#27ae60', 'bold'),
            ('loss', '#e74c3c', 'bold'),
            ('to',   '#e67e22', 'normal'),
            ('val',  '#1a1d23', 'normal'),
            ('lbl',  '#666',    'normal'),
            ('div',  '#ccc',    'normal'),
            ('A',    '#2ecc71', 'bold'),
            ('B',    '#f1c40f', 'bold'),
            ('D',    '#e74c3c', 'bold'),
        ]:
            stats_text.tag_config(tag, foreground=fg,
                                   font=('Consolas', 9 if fw == 'bold' else 8, fw))

        bt_results = {'stats': None, 'trades': []}

        def draw_equity_curve(trades):
            """Draw cumulative P&L curve."""
            eq_fig.clear()
            ax = eq_fig.add_subplot(111)
            ax.set_facecolor('#ffffff')
            eq_fig.patch.set_facecolor('#f8f9fa')

            if not trades:
                ax.text(0.5, 0.5, 'No trades to display',
                        transform=ax.transAxes, ha='center',
                        color='#888', fontsize=10)
                eq_canvas.draw()
                return

            cumulative = [0]
            colors     = []
            for t in trades:
                cumulative.append(cumulative[-1] + t['pnl_pct'])
                colors.append('#2ecc71' if t['hit_target'] else
                              '#e74c3c' if t['hit_stop'] else '#e67e22')

            x = list(range(len(cumulative)))
            # Shade positive/negative
            ax.fill_between(x, cumulative, 0,
                            where=[c >= 0 for c in cumulative],
                            alpha=0.15, color='#2ecc71')
            ax.fill_between(x, cumulative, 0,
                            where=[c < 0 for c in cumulative],
                            alpha=0.15, color='#e74c3c')
            ax.plot(x, cumulative, color='#2471a3', lw=2.0, zorder=3)
            ax.axhline(y=0, color='#888', lw=1.0, linestyle='--')

            # Mark each trade
            for i, t in enumerate(trades):
                col = '#2ecc71' if t['hit_target'] else \
                      '#e74c3c' if t['hit_stop'] else '#e67e22'
                ax.scatter(i+1, cumulative[i+1],
                           color=col, s=30, zorder=4)

            final = cumulative[-1]
            ax.set_title(
                f"Cumulative P&L: {final:+.1f}%  |  "
                f"{len(trades)} trades  |  "
                f"{'▲' if final >= 0 else '▼'} {'Profitable' if final >= 0 else 'Unprofitable'}",
                color='#1a1d23', fontsize=8, pad=4)
            ax.tick_params(colors='#555', labelsize=7)
            ax.set_xlabel('Trade #', color='#555', fontsize=7)
            ax.set_ylabel('Cumulative %', color='#555', fontsize=7)
            for spine in ax.spines.values():
                spine.set_edgecolor('#ccc')
            try:
                eq_fig.tight_layout(pad=0.5)
            except Exception:
                pass
            eq_canvas.draw()

        def show_stats(stats):
            stats_text.config(state='normal')
            stats_text.delete(1.0, tk.END)
            if not stats:
                stats_text.insert(tk.END, "\nNo results yet. Run the backtest.\n", 'lbl')
                stats_text.config(state='disabled')
                return

            stats_text.insert(tk.END, "\n📉  BACKTEST RESULTS\n", 'h1')
            stats_text.insert(tk.END,
                f"    {pat_var.get()}  |  {stats['total']} trades\n\n", 'lbl')

            # Grade
            g = stats['grade']
            g_tag = 'A' if g.startswith('A') else ('B' if g.startswith('B') else 'D')
            stats_text.insert(tk.END, f"  GRADE:  {g}\n\n", g_tag)

            stats_text.insert(tk.END, "─" * 44 + "\n", 'div')
            stats_text.insert(tk.END, "\n  OUTCOME BREAKDOWN\n", 'h2')
            stats_text.insert(tk.END,
                f"  ✅ Hit Target:   {stats['wins']:>3}  ({stats['win_rate']:.1f}%)\n", 'win')
            stats_text.insert(tk.END,
                f"  ❌ Hit Stop:     {stats['losses']:>3}  ({stats['loss_rate']:.1f}%)\n", 'loss')
            stats_text.insert(tk.END,
                f"  ⏱ Timeout:      {stats['timeouts']:>3}  ({stats['timeout_rate']:.1f}%)\n\n", 'to')

            stats_text.insert(tk.END, "  PERFORMANCE\n", 'h2')
            stats_text.insert(tk.END,
                f"  Avg Win:         {stats['avg_win']:>+.2f}%\n", 'win')
            stats_text.insert(tk.END,
                f"  Avg Loss:        {stats['avg_loss']:>+.2f}%\n", 'loss')
            stats_text.insert(tk.END,
                f"  Avg Timeout:     {stats['avg_timeout']:>+.2f}%\n", 'to')
            stats_text.insert(tk.END,
                f"  Avg Hold:        {stats['avg_hold_bars']:.1f} bars\n\n", 'lbl')

            stats_text.insert(tk.END, "  EDGE METRICS\n", 'h2')
            exp = stats['expectancy']
            exp_tag = 'win' if exp > 0 else 'loss'
            stats_text.insert(tk.END,
                f"  Expectancy:      {exp:>+.2f}% per trade\n", exp_tag)
            pf = stats['profit_factor']
            pf_tag = 'win' if pf >= 1.5 else ('to' if pf >= 1.0 else 'loss')
            stats_text.insert(tk.END,
                f"  Profit Factor:   {pf:.2f}x\n\n", pf_tag)

            # Interpretation
            stats_text.insert(tk.END, "─" * 44 + "\n", 'div')
            stats_text.insert(tk.END, "\n  INTERPRETATION\n", 'h2')
            if stats['win_rate'] >= 60 and exp > 2:
                stats_text.insert(tk.END,
                    f"  Strong edge confirmed on this instrument.\n"
                    f"  This pattern is statistically reliable here.\n"
                    f"  Trade with full position when it appears.\n", 'win')
            elif stats['win_rate'] >= 50 and exp >= 0:
                stats_text.insert(tk.END,
                    f"  Marginal edge. Pattern works but not strongly.\n"
                    f"  Use only when other signals confirm.\n"
                    f"  Reduce position size by 30%.\n", 'to')
            else:
                stats_text.insert(tk.END,
                    f"  Negative or no edge on this instrument.\n"
                    f"  Do NOT trade this pattern here.\n"
                    f"  Try a different pattern or more data.\n", 'loss')

            stats_text.config(state='disabled')

        def on_trade_select(event):
            """Show detail for selected trade."""
            sel = lb.curselection()
            if not sel or not bt_results['trades']:
                return
            idx = sel[0]
            if idx >= len(bt_results['trades']):
                return
            t   = bt_results['trades'][idx]
            stats_text.config(state='normal')
            stats_text.delete(1.0, tk.END)
            stats_text.insert(tk.END, f"\n  TRADE #{idx+1} DETAIL\n", 'h1')
            stats_text.insert(tk.END, f"  Date:         {t['entry_date']}\n", 'lbl')
            stats_text.insert(tk.END, f"  Pattern:      {t['pattern']}\n", 'val')
            stats_text.insert(tk.END, f"  Confidence:   {t['confidence']:.1f}%\n", 'lbl')
            stats_text.insert(tk.END, f"  Entry:        {t['entry_price']:.2f}\n", 'val')
            stats_text.insert(tk.END, f"  Stop:         {t['stop_price']:.2f}\n", 'loss')
            stats_text.insert(tk.END, f"  Target:       {t['target_price']:.2f}\n", 'win')
            stats_text.insert(tk.END, f"  Exit:         {t['exit_price']:.2f}\n", 'val')
            stats_text.insert(tk.END, f"  R:R Setup:    1 : {t['rr_setup']:.2f}\n", 'lbl')
            stats_text.insert(tk.END, f"  Bars Held:    {t['bars_held']}\n", 'lbl')
            o_tag = 'win' if t['hit_target'] else ('loss' if t['hit_stop'] else 'to')
            o_sym = '✅' if t['hit_target'] else ('❌' if t['hit_stop'] else '⏱')
            stats_text.insert(tk.END,
                f"  Outcome:      {o_sym} {t['outcome']}\n", o_tag)
            stats_text.insert(tk.END,
                f"  P&L:          {t['pnl_pct']:+.2f}%\n\n", o_tag)
            stats_text.config(state='disabled')

        lb.bind('<<ListboxSelect>>', on_trade_select)

        def run_bt():
            """Run the backtest in the main thread with progress updates."""
            lb.delete(0, tk.END)
            progress_var.set(0)
            status_var.set("⏳ Running backtest... this may take 30–60 seconds.")
            win.update()

            pat      = pat_var.get()
            dirn     = dir_var.get()
            min_conf = conf_var.get()
            max_hold = hold_var.get()

            def update_progress(pct):
                progress_var.set(pct)
                status_var.set(f"⏳ Scanning history... {pct}%")
                win.update_idletasks()

            try:
                trades = run_backtest(
                    self.df, pat, dirn,
                    confidence_threshold=min_conf,
                    max_hold_days=max_hold,
                    progress_cb=update_progress
                )

                if not trades:
                    status_var.set(
                        f"⚠ No trades found for '{pat}' ({dirn}).\n"
                        f"Try: lower confidence threshold, more data, or different pattern.")
                    show_stats(None)
                    draw_equity_curve([])
                    return

                stats = compute_backtest_stats(trades)
                bt_results['stats']  = stats
                bt_results['trades'] = trades

                # Populate trade list
                lb.insert(tk.END,
                    f"  {'#':>3}  {'Date':<12} {'Pat%':>5}  {'P&L':>7}  {'Out':<8}")
                lb.insert(tk.END, "  " + "─" * 46)

                for i, t in enumerate(trades):
                    o_sym = '✅' if t['hit_target'] else \
                            ('❌' if t['hit_stop'] else '⏱')
                    lb.insert(tk.END,
                        f"  {i+1:>3}  {t['entry_date']:<12} "
                        f"{t['confidence']:>4.0f}%  "
                        f"{t['pnl_pct']:>+6.1f}%  "
                        f"{o_sym} {t['outcome']:<7}")

                show_stats(stats)
                draw_equity_curve(trades)
                status_var.set(
                    f"✅ Done — {len(trades)} trades found  |  "
                    f"Win rate: {stats['win_rate']:.1f}%  |  "
                    f"Expectancy: {stats['expectancy']:+.2f}%  |  "
                    f"Grade: {stats['grade'][:2]}")

            except Exception as e:
                import traceback
                status_var.set(f"❌ Error: {str(e)}")
                messagebox.showerror("Backtest Error",
                    f"Backtest failed:\n{str(e)}\n\n{traceback.format_exc()[:300]}")

        # Run button
        tk.Button(settings, text="▶  RUN BACKTEST",
                  command=run_bt,
                  bg=BT_COL, fg='white',
                  font=('Consolas', 11, 'bold'),
                  relief='flat', padx=20, pady=6,
                  cursor='hand2').pack(pady=6)

        # Bottom info
        info = tk.Frame(win, bg=BT_COL, pady=5, padx=16)
        info.pack(fill='x')
        tk.Label(info,
                 text="📉 Backtest scans your loaded OHLC history  "
                      "|  More data = more reliable results  "
                      "|  Recommended: 1–2 years daily data",
                 bg=BT_COL, fg='#f1948a',
                 font=('Consolas', 8)).pack(side='left')

        # Show initial empty state
        show_stats(None)
        draw_equity_curve([])

    def _show_help(self):
        help_win = tk.Toplevel(self.root)
        help_win.title("How to Use + Spyder vs SaaS Explanation")
        help_win.geometry('820x700')
        help_win.configure(bg='#f5f5f5')

        txt = scrolledtext.ScrolledText(help_win, bg='#f5f5f5', fg='#1a1d23',
                                        font=('Consolas', 9), wrap=tk.WORD,
                                        padx=16, pady=12)
        txt.pack(fill='both', expand=True)
        txt.tag_config('h1', foreground='#f1c40f', font=('Consolas', 12, 'bold'))
        txt.tag_config('h2', foreground='#3498db', font=('Consolas', 10, 'bold'))
        txt.tag_config('good', foreground='#2ecc71')
        txt.tag_config('bad', foreground='#e74c3c')
        txt.tag_config('label', foreground='#555555')
        txt.tag_config('value', foreground='#1a1d23')

        content = [
            ("BULKOWSKI CHART PATTERN ANALYZER — HELP\n", 'h1'),
            ("─" * 50 + "\n\n", 'label'),
            ("HOW TO USE THIS APP\n", 'h2'),
            ("1. PREPARE YOUR CSV:\n   Date, Open, High, Low, Close, Volume\n   Column names are case-insensitive\n   Minimum 30 bars recommended, 100+ ideal\n\n", 'value'),
            ("2. LOAD DATA: Click 'Load CSV Data' → select file\n\n", 'value'),
            ("3. DETECT: Click 'Detect Patterns'\n   App scans for 12+ pattern types automatically\n\n", 'value'),
            ("4. SELECT PATTERN from list:\n   Shows confidence %, direction, entry/stop/target\n   Plus Bulkowski's actual statistics from his book\n\n", 'value'),
            ("5. PATTERN LIBRARY: Browse all 53 patterns\n   with full stats even if not auto-detected\n\n", 'value'),
            ("─" * 50 + "\n\n", 'label'),
            ("SPYDER vs SAAS APP — KEY DIFFERENCES\n", 'h1'),
            ("─" * 50 + "\n\n", 'label'),
            ("SPYDER (This App)\n", 'h2'),
            ("  ✅ Runs locally on your laptop — FREE, no server costs\n", 'good'),
            ("  ✅ Your data never leaves your machine — full privacy\n", 'good'),
            ("  ✅ No internet needed after setup\n", 'good'),
            ("  ✅ Unlimited usage — no API limits\n", 'good'),
            ("  ✅ Full code control — modify as you want\n", 'good'),
            ("  ✅ No monthly fees ever\n", 'good'),
            ("  ❌ Only you can use it — not shareable to clients\n", 'bad'),
            ("  ❌ No auto-updates unless you change code\n", 'bad'),
            ("  ❌ No mobile access\n", 'bad'),
            ("  ❌ Need Python knowledge to extend features\n", 'bad'),
            ("  ❌ No real-time data feed built in\n\n", 'bad'),
            ("SAAS APP (FishyBiz / React / Supabase)\n", 'h2'),
            ("  ✅ ANY user (trader) can sign up and use via browser\n", 'good'),
            ("  ✅ Works on phone, tablet, desktop — anywhere\n", 'good'),
            ("  ✅ You can CHARGE users (subscription revenue)\n", 'good'),
            ("  ✅ Real-time data integration possible (broker APIs)\n", 'good'),
            ("  ✅ Multi-tenant: 100 traders using simultaneously\n", 'good'),
            ("  ✅ Automatic updates — push changes for all users\n", 'good'),
            ("  ✅ Analytics: see how users interact with patterns\n", 'good'),
            ("  ❌ Server costs: Supabase + hosting (~₹3000–10,000/mo)\n", 'bad'),
            ("  ❌ More complex to build (auth, payments, APIs)\n", 'bad'),
            ("  ❌ Data security responsibility is yours\n", 'bad'),
            ("  ❌ Requires maintenance and support for users\n\n", 'bad'),
            ("─" * 50 + "\n\n", 'label'),
            ("RECOMMENDATION FOR YOU (JUNAID)\n", 'h1'),
            ("Short term (now): Use this Spyder app for YOUR own\n", 'value'),
            ("  trading research. It's free, private, powerful.\n\n", 'value'),
            ("Medium term: Add chart pattern detection to\n", 'value'),
            ("  FishyBiz SaaS as a feature for fish traders\n", 'value'),
            ("  who trade commodity markets (pepper, turmeric)\n\n", 'value'),
            ("Long term: Build a 'Technical Analysis Module'\n", 'value'),
            ("  in FishyBiz that runs Bulkowski detection on\n", 'value'),
            ("  commodity futures — unique feature for agri traders\n\n", 'value'),
            ("THE PATTERN THIS APP ADDS TO FISHYBIZ:\n", 'h2'),
            ("  Fish commodity prices follow chart patterns\n", 'value'),
            ("  just like stocks. A double bottom in pomfret\n", 'value'),
            ("  wholesale prices is a genuine buy signal for\n", 'value'),
            ("  your VAR Fisheries procurement decisions.\n", 'value'),
            ("  That's a real business use case for this tool.\n", 'value'),
        ]

        for text, tag in content:
            txt.insert(tk.END, text, tag)

        txt.config(state='disabled')


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    root.resizable(True, True)
    app = BulkowskiApp(root)

    # Center window
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f'{w}x{h}+{x}+{y}')

    root.mainloop()


if __name__ == '__main__':
    main()
