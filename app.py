# app.py
# Simple unit converter using Gradio (ready for Hugging Face Spaces).
# No !pip installs here — Spaces installs packages from requirements.txt.

import gradio as gr

# === Unit maps ===
UNIT_FACTORS = {
    "Length": {
        "meter (m)": 1.0,
        "centimeter (cm)": 0.01,
        "millimeter (mm)": 0.001,
        "kilometer (km)": 1000.0,
        "inch (in)": 0.0254,
        "foot (ft)": 0.3048,
        "yard (yd)": 0.9144,
        "mile (mi)": 1609.344,
    },
    "Mass": {
        "kilogram (kg)": 1.0,
        "gram (g)": 0.001,
        "milligram (mg)": 1e-6,
        "tonne (t)": 1000.0,
        "pound (lb)": 0.45359237,
        "ounce (oz)": 0.028349523125,
    },
    "Volume": {
        "liter (L)": 1.0,
        "milliliter (mL)": 0.001,
        "cubic meter (m³)": 1000.0,
        "US cup": 0.2365882365,
        "US fl oz": 0.0295735295625,
        "US gallon": 3.785411784,
    },
    "Time": {
        "second (s)": 1.0,
        "minute (min)": 60.0,
        "hour (h)": 3600.0,
        "day": 86400.0,
    }
}

TEMPERATURE_UNITS = ["Celsius (°C)", "Fahrenheit (°F)", "Kelvin (K)"]

# === Conversion helpers ===
def convert_temperature(value: float, frm: str, to: str, decimals: int) -> str:
    if "Celsius" in frm:
        c = value
    elif "Fahrenheit" in frm:
        c = (value - 32.0) * 5.0/9.0
    elif "Kelvin" in frm:
        c = value - 273.15
    else:
        return "Unknown source temperature unit."

    if "Celsius" in to:
        out = c
    elif "Fahrenheit" in to:
        out = c * 9.0/5.0 + 32.0
    elif "Kelvin" in to:
        out = c + 273.15
    else:
        return "Unknown target temperature unit."

    return f"{value} {frm} = {round(out, decimals)} {to}"

def convert_generic(value: float, category: str, frm: str, to: str, decimals: int) -> str:
    factors = UNIT_FACTORS.get(category)
    if factors is None:
        return "Unknown category."
    try:
        f_from = factors[frm]
        f_to   = factors[to]
    except KeyError:
        return "Unit not available in that category."

    base_value = value * f_from
    result = base_value / f_to
    return f"{value} {frm} = {round(result, decimals)} {to}"

def convert(value, category, frm, to, decimals):
    try:
        value = float(value)
    except Exception:
        return "Please enter a valid numeric value."

    if category == "Temperature":
        return convert_temperature(value, frm, to, decimals)
    else:
        return convert_generic(value, category, frm, to, decimals)

# === Gradio UI ===
with gr.Blocks() as demo:
    gr.Markdown("## 🧮 Simple Unit Converter (Hugging Face Space)\n"
                "Choose a category, enter a value, pick units and click **Convert**.")
    with gr.Row():
        category = gr.Dropdown(choices=list(list(UNIT_FACTORS.keys()) + ["Temperature"]),
                               value="Length", label="Category")
        decimals = gr.Slider(minimum=0, maximum=8, step=1, value=4, label="Decimal places")

    initial_units = list(UNIT_FACTORS["Length"].keys())
    from_unit = gr.Dropdown(choices=initial_units, value=initial_units[0], label="From unit")
    to_unit   = gr.Dropdown(choices=initial_units, value=initial_units[1], label="To unit")

    value_in = gr.Number(value=1.0, label="Value to convert")
    result_out = gr.Textbox(label="Result", interactive=False)

    with gr.Row():
        convert_btn = gr.Button("Convert")
        swap_btn = gr.Button("Swap From/To")

    def update_unit_dropdowns(cat):
        if cat == "Temperature":
            opts = TEMPERATURE_UNITS
        else:
            opts = list(UNIT_FACTORS.get(cat, {}).keys())
        default_to = opts[1] if len(opts) > 1 else opts[0]
        return gr.update(choices=opts, value=opts[0]), gr.update(choices=opts, value=default_to)

    category.change(fn=update_unit_dropdowns, inputs=category, outputs=[from_unit, to_unit])

    def swap(frm, to):
        return to, frm
    swap_btn.click(fn=swap, inputs=[from_unit, to_unit], outputs=[from_unit, to_unit])

    convert_btn.click(fn=convert,
                      inputs=[value_in, category, from_unit, to_unit, decimals],
                      outputs=result_out)

# For Spaces we can simply call launch() here.
if __name__ == "__main__":
    demo.launch()
