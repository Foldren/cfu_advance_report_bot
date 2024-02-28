from dataclasses import dataclass
from aiogram.utils.markdown import hitalic, hcode, hbold


@dataclass
class Text:
    hint_p_from_new_str: str = hitalic("(каждый параметр вводите с новой строки, как в примере ниже)")

    @staticmethod
    def example(*params):
        elements = []
        e_params = ""

        for i, p in enumerate(params):
            if p == "":
                elements.append(e_params[:-1])
                e_params = ""
            elif i == len(params) - 1:
                e_params += p
                elements.append(e_params)
                break
            else:
                e_params += p + "\n"

        result = hbold("Пример") + " (просто нажмите 👇):\n" + "\n\n".join([hcode(params) for params in elements])

        return result

    @staticmethod
    def title(text: str, step: int = None):
        step_text = f": (шаг {step})" if step is not None else ""
        return hbold(text + step_text)
