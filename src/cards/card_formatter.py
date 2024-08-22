from termcolor import colored
import re
class CardFormatter:
    # Symbol and color mapping
    SYMBOL_MAP = {
        "[click]": "🕒",
        "[credit]": "💰",
        "[trash]": "🗑️",
        "[recurring-credit]": "🔄💰",
        "[mu]": "🧠",
        "[link]": "🔗",
        "[subroutine]": "⊡",
    }

    COLOR_MAP = {
        "click": "cyan",
        "credit": "yellow",
        "trash": "red",
        "recurring-credit": "yellow",
        "mu": "magenta",
        "link": "blue",
        "subroutine": "green",
    }

    @staticmethod
    def apply_formatting(text):
        for symbol, replacement in CardFormatter.SYMBOL_MAP.items():
            text = text.replace(symbol, replacement)
        
        for resource, color in CardFormatter.COLOR_MAP.items():
            pattern = r'\[' + resource + r'\]'
            text = re.sub(pattern, lambda m: colored(CardFormatter.SYMBOL_MAP.get(m.group(), m.group()), color), text)
        
        text = re.sub(r'<strong>(.*?)</strong>', lambda m: colored(m.group(1), 'white', attrs=['bold']), text)
        return text