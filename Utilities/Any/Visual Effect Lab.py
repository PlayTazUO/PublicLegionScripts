"""
VFX Lab - experiment with the Legion VisualEffects and ScreenShake APIs.

Tune the controls, click Apply & Start to see the result, then copy the generated
code from the right-hand panel (or print it to the journal) into your own script.

The client ships with visual effects and screen shake turned off. Enable them under
Options > Video > Visual Effects first, or Start will quietly return 0.

Photosensitive epilepsy warning: visual effects and shake can flash or move the
screen. Avoid starting and stopping an effect in a tight loop.
"""

import time

import API

# ---------------------------------------------------------------------------
# API defaults and small helpers
# ---------------------------------------------------------------------------

_DEFAULT_PROFILE = API.VisualEffects.NewProfile()
_DEFAULT_LAYER = API.VisualEffects.NewTintLayer()
_DEFAULT_BLUR = API.VisualEffects.NewBlurLayer()
_DEFAULT_RADIAL = API.VisualEffects.NewRadialBlurLayer()
_DEFAULT_CHROMATIC = API.VisualEffects.NewChromaticLayer()
_DEFAULT_SPEC = API.VisualEffects.NewShakeSpec()
_DEFAULT_CONFIG = API.VisualEffects.NewShakeConfig()

DEFAULT_FADE_IN = _DEFAULT_PROFILE.Fade.InSeconds
DEFAULT_FADE_OUT = _DEFAULT_PROFILE.Fade.OutSeconds
DEFAULT_STRENGTH = _DEFAULT_LAYER.Strength

DEFAULT_SHAPE_REACH = _DEFAULT_LAYER.Shape.Reach
DEFAULT_SHAPE_FEATHER = _DEFAULT_LAYER.Shape.Feather
DEFAULT_SHAPE_EDGE = _DEFAULT_LAYER.Shape.EdgeBlend
DEFAULT_SHAPE_CORNER = _DEFAULT_LAYER.Shape.CornerBias
DEFAULT_SHAPE_WOBBLE = _DEFAULT_LAYER.Shape.WobbleAmp
DEFAULT_JITTER_REACH = _DEFAULT_LAYER.Shape.Jitter.ReachAmount
DEFAULT_JITTER_FEATHER = _DEFAULT_LAYER.Shape.Jitter.FeatherAmount

DEFAULT_NOISE_BASE_X = _DEFAULT_LAYER.Noise.BaseScale.X
DEFAULT_NOISE_BASE_Y = _DEFAULT_LAYER.Noise.BaseScale.Y
DEFAULT_NOISE_SCROLL_X = _DEFAULT_LAYER.Noise.BaseScroll.X
DEFAULT_NOISE_SCROLL_Y = _DEFAULT_LAYER.Noise.BaseScroll.Y
DEFAULT_NOISE_WARP = _DEFAULT_LAYER.Noise.WarpStrength
DEFAULT_NOISE_RIDGE = _DEFAULT_LAYER.Noise.RidgeAmount
DEFAULT_NOISE_THRESHOLD = _DEFAULT_LAYER.Noise.Threshold
DEFAULT_NOISE_SOFTNESS = _DEFAULT_LAYER.Noise.Softness
DEFAULT_NOISE_FLAT = _DEFAULT_LAYER.Noise.FlatFloor

DEFAULT_TINT_R = _DEFAULT_LAYER.R
DEFAULT_TINT_G = _DEFAULT_LAYER.G
DEFAULT_TINT_B = _DEFAULT_LAYER.B
DEFAULT_TINT_A = _DEFAULT_LAYER.A

DEFAULT_BLUR_RADIUS = _DEFAULT_BLUR.Radius
DEFAULT_RADIAL_ZOOM = _DEFAULT_RADIAL.Zoom
DEFAULT_CHROMATIC_ABERRATION = _DEFAULT_CHROMATIC.Aberration

DEFAULT_SHAKE_TRAUMA = _DEFAULT_SPEC.Trauma
DEFAULT_SHAKE_SECONDS = _DEFAULT_SPEC.DurationSeconds
DEFAULT_SHAKE_RAMP_UP = _DEFAULT_SPEC.RampUpSeconds
DEFAULT_SHAKE_RAMP_DOWN = _DEFAULT_SPEC.RampDownSeconds
DEFAULT_SHAKE_FREQUENCY = _DEFAULT_SPEC.Frequency

DEFAULT_CONFIG_SECONDS = _DEFAULT_CONFIG.Seconds
DEFAULT_CONFIG_INTENSITY = _DEFAULT_CONFIG.Intensity
DEFAULT_CONFIG_RAMP_UP = _DEFAULT_CONFIG.RampUpSeconds
DEFAULT_CONFIG_RAMP_DOWN = _DEFAULT_CONFIG.RampDownSeconds
DEFAULT_CONFIG_FREQUENCY = _DEFAULT_CONFIG.Frequency
DEFAULT_CONFIG_MAX_OFFSET = _DEFAULT_CONFIG.MaxOffsetPixels

LAYER_NAMES = ["Tint", "Disk blur", "Radial blur", "Chromatic"]
LAYER_FACTORIES = ["NewTintLayer", "NewBlurLayer", "NewRadialBlurLayer", "NewChromaticLayer"]

BLEND_NAMES = ["Alpha", "Additive"]
BLEND_VALUES = [
    API.VisualEffects.OverlayBlend.Alpha,
    API.VisualEffects.OverlayBlend.Additive,
]

TAP_NAMES = ["Four", "Eight", "Twelve", "Sixteen"]
TAP_VALUES = [
    API.VisualEffects.OverlaySampleTaps.Four,
    API.VisualEffects.OverlaySampleTaps.Eight,
    API.VisualEffects.OverlaySampleTaps.Twelve,
    API.VisualEffects.OverlaySampleTaps.Sixteen,
]
DEFAULT_BLUR_TAPS = 2
DEFAULT_RADIAL_TAPS = 1

CHANNEL_NAMES = ["Red", "Green", "Blue", "Alpha"]
CHANNEL_VALUES = [
    API.VisualEffects.NoiseChannel.Red,
    API.VisualEffects.NoiseChannel.Green,
    API.VisualEffects.NoiseChannel.Blue,
    API.VisualEffects.NoiseChannel.Alpha,
]
CHANNEL_LABELS = [
    "Red - soft fBm",
    "Green - fine fBm",
    "Blue - ridged filaments",
    "Alpha - cell edges",
]
DEFAULT_BASE_CHANNEL = 0
DEFAULT_DETAIL_CHANNEL = 1

GRADIENT_NAMES = ["Constant", "Decay", "Swell", "Pulse"]
GRADIENT_VALUES = [
    API.VisualEffects.ShakeGradient.Constant,
    API.VisualEffects.ShakeGradient.Decay,
    API.VisualEffects.ShakeGradient.Swell,
    API.VisualEffects.ShakeGradient.Pulse,
]

CURVE_NAMES = ["Linear", "Smooth", "EaseIn", "EaseOut"]
CURVE_VALUES = [
    API.VisualEffects.ShakeCurve.Linear,
    API.VisualEffects.ShakeCurve.Smooth,
    API.VisualEffects.ShakeCurve.EaseIn,
    API.VisualEffects.ShakeCurve.EaseOut,
]
DEFAULT_ATTACHED_CURVE = 2
DEFAULT_STANDALONE_CURVE = 0

# UO hue used for the checkbox text. 987 is a readable pale hue; 996 also works.
CHECKBOX_HUE = 987


def _number(value):
    """Compact numeric text, so the generated snippet stays short."""
    value = float(value)
    if abs(value) < 0.0000001:
        return "0"

    text = ("%.4f" % value).rstrip("0").rstrip(".")
    return text if text else "0"


def _percent(value):
    return "%d%%" % value


def _hundredths_seconds(value):
    return "%.2fs" % (value / 100.0)


def _one_decimal(value):
    return "%.1f" % (value / 10.0)


def _two_decimals(value):
    return "%.2f" % (value / 100.0)


def _hundredths_hz(value):
    return "%.2f Hz" % (value / 100.0)


def _radius(value):
    return "%.3f" % (value / 10000.0)


def _duration(value):
    return "until stopped" if value <= 0 else "%ds" % value


def _shake_frequency(value):
    return "default" if value == 0 else "%.2f Hz" % (value / 100.0)


# ---------------------------------------------------------------------------
# UI plumbing
# ---------------------------------------------------------------------------

WINDOW_W = 900
WINDOW_H = 748
CONTENT_W = 480
LABEL_X = 8
LABEL_W = 200
SLIDER_X = 220
SLIDER_W = 260
DROPDOWN_X = 205
DROPDOWN_W = 265

state = {}
rows = []
preview_dirty = True
last_code = ""
status_text = ""
status_hold_until = 0


def mark_dirty():
    global preview_dirty
    preview_dirty = True


class Row:
    def __init__(self, group, height):
        self.group = group
        self.height = height
        self.controls = []

    def add_control(self, control):
        self.controls.append(control)

    def set_visible(self, visible):
        for control in self.controls:
            control.IsVisible = visible


class HeaderRow(Row):
    def __init__(self, text, group):
        Row.__init__(self, group, 30)
        self.label = API.Gumps.CreateGumpTTFLabel(text, 15, "#FFFFFF", maxWidth=CONTENT_W)
        self.label.SetRect(0, 0, CONTENT_W, 22)
        self.add_control(self.label)

    def place(self, y):
        self.label.SetPos(LABEL_X, y + 4)


class SliderRow(Row):
    def __init__(
        self,
        parent,
        key,
        title,
        minimum,
        maximum,
        initial,
        scale=0.01,
        formatter=None,
        group="effect",
        tooltip=None,
    ):
        Row.__init__(self, group, 32)
        self.key = key
        self.title = title
        self.scale = scale
        self.formatter = formatter

        raw = int(round(initial / scale))
        raw = max(minimum, min(maximum, raw))
        state[key] = raw * scale

        self.label = API.Gumps.CreateGumpTTFLabel("", 13, "#FFFFFF", aligned="left", maxWidth=LABEL_W)
        self.label.SetRect(0, 0, LABEL_W, 22)
        self.slider = API.Gumps.CreateSlider(SLIDER_W, minimum, maximum, raw, 0, 0, False)
        parent.Add(self.label)
        parent.Add(self.slider)
        self.add_control(self.label)
        self.add_control(self.slider)

        if tooltip:
            self.slider.SetTooltip(tooltip)

        self.slider.OnValueChanged(self._changed)
        self._show_value(raw)

    def _changed(self, value):
        state[self.key] = value * self.scale
        self._show_value(value)
        mark_dirty()

    def _show_value(self, value):
        text = self.formatter(value) if self.formatter else str(value)
        self.label.SetText("%s: %s" % (self.title, text))

    def place(self, y):
        self.label.SetPos(LABEL_X, y + 5)
        self.slider.SetPos(SLIDER_X, y + 3)


class DropdownRow(Row):
    def __init__(self, parent, key, title, options, selected=0, group="effect", on_change=None, tooltip=None):
        Row.__init__(self, group, 34)
        self.key = key
        self.on_change = on_change
        state[key] = selected

        self.label = API.Gumps.CreateGumpTTFLabel(title, 13, "#FFFFFF", aligned="left", maxWidth=180)
        self.label.SetRect(0, 0, 180, 22)
        self.dropdown = API.Gumps.CreateDropDown(DROPDOWN_W, options, selected)
        parent.Add(self.label)
        parent.Add(self.dropdown)
        self.add_control(self.label)
        self.add_control(self.dropdown)

        if tooltip:
            self.dropdown.SetTooltip(tooltip)

        self.dropdown.OnDropDownOptionSelected(self._changed)

    def _changed(self, index):
        state[self.key] = index
        if self.on_change:
            self.on_change(index)
        mark_dirty()

    def place(self, y):
        self.label.SetPos(LABEL_X, y + 6)
        self.dropdown.SetPos(DROPDOWN_X, y + 2)


class CheckboxRow(Row):
    def __init__(self, parent, key, text, checked=False, group="always", on_change=None, tooltip=None):
        Row.__init__(self, group, 28)
        self.key = key
        self.on_change = on_change
        state[key] = checked

        self.checkbox = API.Gumps.CreateGumpCheckbox(text, CHECKBOX_HUE, checked)
        self.checkbox.SetRect(0, 0, CONTENT_W, 24)
        parent.Add(self.checkbox)
        self.add_control(self.checkbox)

        if tooltip:
            self.checkbox.SetTooltip(tooltip)

        API.Gumps.AddControlOnClick(self.checkbox, self._clicked)

    def _clicked(self):
        # Derive the new value ourselves instead of trusting the click ordering.
        value = not state[self.key]
        state[self.key] = value
        self.checkbox.SetIsChecked(value)
        if self.on_change:
            self.on_change(value)
        mark_dirty()

    def place(self, y):
        self.checkbox.SetPos(LABEL_X, y + 2)


def group_visible(group):
    if group == "always":
        return True
    if group == "effect":
        return state["effect_on"]
    if group == "tint":
        return state["effect_on"] and state["layer_kind"] == 0
    if group == "blur":
        return state["effect_on"] and state["layer_kind"] == 1
    if group == "radial":
        return state["effect_on"] and state["layer_kind"] == 2
    if group == "chromatic":
        return state["effect_on"] and state["layer_kind"] == 3
    if group == "pulse":
        return state["effect_on"] and state["pulse_on"]
    if group == "advanced_shape":
        return state["effect_on"] and state["advanced_shape"]
    if group == "advanced_noise":
        return state["effect_on"] and state["advanced_noise"]
    if group == "shake_mode":
        return state["shake_on"] and state["effect_on"]
    if group == "shake_details":
        return state["shake_on"]
    if group == "shake_standalone":
        return state["shake_on"] and (not state["effect_on"] or state["shake_mode"] == 1)
    return False


def layout_rows():
    y = 4
    for row in rows:
        visible = group_visible(row.group)
        row.set_visible(visible)
        if visible:
            row.place(y)
            y += row.height


def set_status(text, hold_seconds=0):
    global status_text, status_hold_until
    if text == status_text:
        return

    status_text = text
    status_hold_until = time.time() + hold_seconds
    status_label.SetText(text)


def refresh_status():
    if time.time() < status_hold_until:
        return

    effects = "ON" if API.VisualEffects.Enabled else "OFF"
    shake = "ON" if API.VisualEffects.ShakeEnabled else "OFF"
    text = "Effects: %s   Shake: %s   Free slots: %d   -   Click Apply to see changes" % (
        effects,
        shake,
        API.VisualEffects.SlotsFree,
    )
    if not API.VisualEffects.Enabled:
        text += "   (Options > Video > Visual Effects)"

    set_status(text)


# ---------------------------------------------------------------------------
# Turning the UI state into API objects and into copyable code
# ---------------------------------------------------------------------------


def build_layer():
    kind = state["layer_kind"]

    if kind == 0:
        layer = API.VisualEffects.NewTintLayer()
        layer.R = int(state["tint_r"])
        layer.G = int(state["tint_g"])
        layer.B = int(state["tint_b"])
        layer.A = int(state["tint_a"])
    elif kind == 1:
        layer = API.VisualEffects.NewBlurLayer()
        layer.Radius = state["blur_radius"]
        layer.Taps = TAP_VALUES[state["blur_taps"]]
    elif kind == 2:
        layer = API.VisualEffects.NewRadialBlurLayer()
        layer.Zoom = state["radial_zoom"]
        layer.Taps = TAP_VALUES[state["radial_taps"]]
    else:
        layer = API.VisualEffects.NewChromaticLayer()
        layer.Aberration = state["chromatic_aberration"]

    layer.Strength = state["strength"]

    if state["pulse_on"]:
        layer.Pulse.Frequency = state["pulse_frequency"]
        layer.Pulse.Amplitude = state["pulse_amplitude"]

    shape = layer.Shape
    shape.Reach = state["shape_reach"]
    shape.Feather = state["shape_feather"]
    shape.EdgeBlend = state["shape_edge"]
    shape.CornerBias = state["shape_corner"]
    shape.WobbleAmp = state["shape_wobble"]
    shape.Jitter.ReachAmount = state["jitter_reach"]
    shape.Jitter.FeatherAmount = state["jitter_feather"]

    noise = layer.Noise
    noise.BaseScale = API.VisualEffects.NewVector2(state["noise_base_x"], state["noise_base_y"])
    noise.BaseScroll = API.VisualEffects.NewVector2(state["noise_scroll_x"], state["noise_scroll_y"])
    noise.BaseChannel = CHANNEL_VALUES[state["base_channel"]]
    noise.DetailChannel = CHANNEL_VALUES[state["detail_channel"]]
    noise.WarpStrength = state["noise_warp"]
    noise.RidgeAmount = state["noise_ridge"]
    noise.Threshold = state["noise_threshold"]
    noise.Softness = state["noise_softness"]
    noise.FlatFloor = state["noise_flat"]

    return layer


def build_attached_shake():
    shake = API.VisualEffects.NewShakeSpec()
    shake.Trauma = state["shake_trauma"]
    shake.DurationSeconds = state["shake_seconds"]
    shake.RampUpSeconds = state["shake_ramp_up"]
    shake.RampDownSeconds = state["shake_ramp_down"]
    shake.Frequency = state["shake_frequency"]
    shake.Curve = CURVE_VALUES[state["shake_curve"]]
    return shake


def build_standalone_shake():
    shake = API.VisualEffects.NewShakeConfig()
    shake.Seconds = max(state["shake_seconds"], 0.01)
    shake.Intensity = state["shake_trauma"]
    shake.RampUpSeconds = state["shake_ramp_up"]
    shake.RampDownSeconds = state["shake_ramp_down"]
    shake.Gradient = GRADIENT_VALUES[state["shake_gradient"]]
    shake.Curve = CURVE_VALUES[state["shake_curve"]]
    shake.Frequency = state["shake_frequency"]
    shake.MaxOffsetPixels = state["shake_max_offset"]
    shake.FullScreen = state["shake_fullscreen"]
    return shake


def build_effect():
    effect = API.VisualEffects.NewProfile()
    effect.FullScreen = state["effect_fullscreen"]
    effect.Fade.InSeconds = state["fade_in"]
    effect.Fade.OutSeconds = state["fade_out"]

    layer = build_layer()
    effect.AddLayer(layer, BLEND_VALUES[state["blend"]])

    if state["shake_on"] and state["shake_mode"] == 0:
        effect.Shake = build_attached_shake()

    return effect


class CodeBuilder:
    def __init__(self):
        self.lines = []
        self.depth = 0

    def add(self, text=""):
        self.lines.append("    " * self.depth + text)

    def text(self):
        return "\n".join(self.lines)


def add_changed_float(builder, target, value, default):
    if abs(value - default) > 0.000001:
        builder.add("%s = %s" % (target, _number(value)))


def add_changed_enum(builder, target, index, default_index, names, prefix):
    if index != default_index:
        builder.add("%s = %s.%s" % (target, prefix, names[index]))


def add_effect_code(builder, include_attached_shake):
    builder.add("effect = API.VisualEffects.NewProfile()")

    if state["effect_fullscreen"]:
        builder.add("effect.FullScreen = True")

    add_changed_float(builder, "effect.Fade.InSeconds", state["fade_in"], DEFAULT_FADE_IN)
    add_changed_float(builder, "effect.Fade.OutSeconds", state["fade_out"], DEFAULT_FADE_OUT)

    kind = state["layer_kind"]
    builder.add("layer = API.VisualEffects.%s()" % LAYER_FACTORIES[kind])

    if kind == 0:
        add_changed_float(builder, "layer.R", state["tint_r"], DEFAULT_TINT_R)
        add_changed_float(builder, "layer.G", state["tint_g"], DEFAULT_TINT_G)
        add_changed_float(builder, "layer.B", state["tint_b"], DEFAULT_TINT_B)
        add_changed_float(builder, "layer.A", state["tint_a"], DEFAULT_TINT_A)
    elif kind == 1:
        add_changed_float(builder, "layer.Radius", state["blur_radius"], DEFAULT_BLUR_RADIUS)
        add_changed_enum(
            builder,
            "layer.Taps",
            state["blur_taps"],
            DEFAULT_BLUR_TAPS,
            TAP_NAMES,
            "API.VisualEffects.OverlaySampleTaps",
        )
    elif kind == 2:
        add_changed_float(builder, "layer.Zoom", state["radial_zoom"], DEFAULT_RADIAL_ZOOM)
        add_changed_enum(
            builder,
            "layer.Taps",
            state["radial_taps"],
            DEFAULT_RADIAL_TAPS,
            TAP_NAMES,
            "API.VisualEffects.OverlaySampleTaps",
        )
    else:
        add_changed_float(builder, "layer.Aberration", state["chromatic_aberration"], DEFAULT_CHROMATIC_ABERRATION)

    add_changed_float(builder, "layer.Strength", state["strength"], DEFAULT_STRENGTH)

    if state["pulse_on"]:
        builder.add("layer.Pulse.Frequency = %s" % _number(state["pulse_frequency"]))
        builder.add("layer.Pulse.Amplitude = %s" % _number(state["pulse_amplitude"]))

    shape_changed = (
        abs(state["shape_reach"] - DEFAULT_SHAPE_REACH) > 0.000001
        or abs(state["shape_feather"] - DEFAULT_SHAPE_FEATHER) > 0.000001
        or abs(state["shape_edge"] - DEFAULT_SHAPE_EDGE) > 0.000001
        or abs(state["shape_corner"] - DEFAULT_SHAPE_CORNER) > 0.000001
        or abs(state["shape_wobble"] - DEFAULT_SHAPE_WOBBLE) > 0.000001
        or abs(state["jitter_reach"] - DEFAULT_JITTER_REACH) > 0.000001
        or abs(state["jitter_feather"] - DEFAULT_JITTER_FEATHER) > 0.000001
    )
    if shape_changed:
        builder.add("shape = layer.Shape")
        add_changed_float(builder, "shape.Reach", state["shape_reach"], DEFAULT_SHAPE_REACH)
        add_changed_float(builder, "shape.Feather", state["shape_feather"], DEFAULT_SHAPE_FEATHER)
        add_changed_float(builder, "shape.EdgeBlend", state["shape_edge"], DEFAULT_SHAPE_EDGE)
        add_changed_float(builder, "shape.CornerBias", state["shape_corner"], DEFAULT_SHAPE_CORNER)
        add_changed_float(builder, "shape.WobbleAmp", state["shape_wobble"], DEFAULT_SHAPE_WOBBLE)
        add_changed_float(builder, "shape.Jitter.ReachAmount", state["jitter_reach"], DEFAULT_JITTER_REACH)
        add_changed_float(builder, "shape.Jitter.FeatherAmount", state["jitter_feather"], DEFAULT_JITTER_FEATHER)

    noise_changed = (
        abs(state["noise_base_x"] - DEFAULT_NOISE_BASE_X) > 0.000001
        or abs(state["noise_base_y"] - DEFAULT_NOISE_BASE_Y) > 0.000001
        or abs(state["noise_scroll_x"] - DEFAULT_NOISE_SCROLL_X) > 0.000001
        or abs(state["noise_scroll_y"] - DEFAULT_NOISE_SCROLL_Y) > 0.000001
        or abs(state["noise_warp"] - DEFAULT_NOISE_WARP) > 0.000001
        or abs(state["noise_ridge"] - DEFAULT_NOISE_RIDGE) > 0.000001
        or abs(state["noise_threshold"] - DEFAULT_NOISE_THRESHOLD) > 0.000001
        or abs(state["noise_softness"] - DEFAULT_NOISE_SOFTNESS) > 0.000001
        or abs(state["noise_flat"] - DEFAULT_NOISE_FLAT) > 0.000001
        or state["base_channel"] != DEFAULT_BASE_CHANNEL
        or state["detail_channel"] != DEFAULT_DETAIL_CHANNEL
    )
    if noise_changed:
        builder.add("noise = layer.Noise")
        if (
            abs(state["noise_base_x"] - DEFAULT_NOISE_BASE_X) > 0.000001
            or abs(state["noise_base_y"] - DEFAULT_NOISE_BASE_Y) > 0.000001
        ):
            builder.add(
                "noise.BaseScale = API.VisualEffects.NewVector2(%s, %s)"
                % (_number(state["noise_base_x"]), _number(state["noise_base_y"]))
            )
        if (
            abs(state["noise_scroll_x"] - DEFAULT_NOISE_SCROLL_X) > 0.000001
            or abs(state["noise_scroll_y"] - DEFAULT_NOISE_SCROLL_Y) > 0.000001
        ):
            builder.add(
                "noise.BaseScroll = API.VisualEffects.NewVector2(%s, %s)"
                % (_number(state["noise_scroll_x"]), _number(state["noise_scroll_y"]))
            )
        add_changed_enum(
            builder,
            "noise.BaseChannel",
            state["base_channel"],
            DEFAULT_BASE_CHANNEL,
            CHANNEL_NAMES,
            "API.VisualEffects.NoiseChannel",
        )
        add_changed_enum(
            builder,
            "noise.DetailChannel",
            state["detail_channel"],
            DEFAULT_DETAIL_CHANNEL,
            CHANNEL_NAMES,
            "API.VisualEffects.NoiseChannel",
        )
        add_changed_float(builder, "noise.WarpStrength", state["noise_warp"], DEFAULT_NOISE_WARP)
        add_changed_float(builder, "noise.RidgeAmount", state["noise_ridge"], DEFAULT_NOISE_RIDGE)
        add_changed_float(builder, "noise.Threshold", state["noise_threshold"], DEFAULT_NOISE_THRESHOLD)
        add_changed_float(builder, "noise.Softness", state["noise_softness"], DEFAULT_NOISE_SOFTNESS)
        add_changed_float(builder, "noise.FlatFloor", state["noise_flat"], DEFAULT_NOISE_FLAT)

    if state["blend"] == 0:
        builder.add("effect.AddLayer(layer)")
    else:
        builder.add("effect.AddLayer(layer, API.VisualEffects.OverlayBlend.Additive)")

    if include_attached_shake:
        builder.add("shake = API.VisualEffects.NewShakeSpec()")
        add_changed_float(builder, "shake.Trauma", state["shake_trauma"], DEFAULT_SHAKE_TRAUMA)
        add_changed_float(builder, "shake.DurationSeconds", state["shake_seconds"], DEFAULT_SHAKE_SECONDS)
        add_changed_float(builder, "shake.RampUpSeconds", state["shake_ramp_up"], DEFAULT_SHAKE_RAMP_UP)
        add_changed_float(builder, "shake.RampDownSeconds", state["shake_ramp_down"], DEFAULT_SHAKE_RAMP_DOWN)
        add_changed_float(builder, "shake.Frequency", state["shake_frequency"], DEFAULT_SHAKE_FREQUENCY)
        add_changed_enum(
            builder,
            "shake.Curve",
            state["shake_curve"],
            DEFAULT_ATTACHED_CURVE,
            CURVE_NAMES,
            "API.VisualEffects.ShakeCurve",
        )
        builder.add("effect.Shake = shake")

    builder.add(
        "handle = API.VisualEffects.Start(effect, %s, %s)"
        % (_number(state["seconds"]), _number(state["intensity"]))
    )


def add_standalone_shake_code(builder):
    builder.add("shake = API.VisualEffects.NewShakeConfig()")
    add_changed_float(builder, "shake.Seconds", state["shake_seconds"], DEFAULT_CONFIG_SECONDS)
    add_changed_float(builder, "shake.Intensity", state["shake_trauma"], DEFAULT_CONFIG_INTENSITY)
    add_changed_float(builder, "shake.RampUpSeconds", state["shake_ramp_up"], DEFAULT_CONFIG_RAMP_UP)
    add_changed_float(builder, "shake.RampDownSeconds", state["shake_ramp_down"], DEFAULT_CONFIG_RAMP_DOWN)
    add_changed_enum(
        builder,
        "shake.Gradient",
        state["shake_gradient"],
        0,
        GRADIENT_NAMES,
        "API.VisualEffects.ShakeGradient",
    )
    add_changed_enum(
        builder,
        "shake.Curve",
        state["shake_curve"],
        DEFAULT_STANDALONE_CURVE,
        CURVE_NAMES,
        "API.VisualEffects.ShakeCurve",
    )
    add_changed_float(builder, "shake.Frequency", state["shake_frequency"], DEFAULT_CONFIG_FREQUENCY)
    add_changed_float(builder, "shake.MaxOffsetPixels", state["shake_max_offset"], DEFAULT_CONFIG_MAX_OFFSET)
    if state["shake_fullscreen"]:
        builder.add("shake.FullScreen = True")

    builder.add("shake_handle = API.VisualEffects.StartShake(shake)")


def build_code():
    if not state["effect_on"] and not state["shake_on"]:
        return "# Turn on the visual effect or the screen shake in VFX Lab first."

    standalone_shake = state["shake_on"] and (not state["effect_on"] or state["shake_mode"] == 1)
    attached_shake = state["shake_on"] and state["effect_on"] and state["shake_mode"] == 0

    builder = CodeBuilder()
    builder.add("# Paste this into your Legion script.")
    builder.add("def start_vfx():")
    builder.depth = 1

    if state["effect_on"]:
        add_effect_code(builder, attached_shake)

    if standalone_shake:
        add_standalone_shake_code(builder)

    if state["effect_on"]:
        builder.add("return handle")
    else:
        builder.add("return shake_handle")

    return builder.text()


def refresh_preview():
    global preview_dirty, last_code
    code = build_code()
    if code != last_code:
        last_code = code
        code_box.SetText(code)
    preview_dirty = False


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------


def apply_settings():
    set_status("Starting...", 2)

    try:
        API.VisualEffects.StopAll()
        API.VisualEffects.StopAllShakes()

        started = []
        effect_handle = 0

        if state["effect_on"]:
            effect_handle = API.VisualEffects.Start(
                build_effect(),
                state["seconds"],
                state["intensity"],
            )
            if effect_handle:
                started.append("effect")

        if state["shake_on"] and (not state["effect_on"] or state["shake_mode"] == 1):
            shake_handle = API.VisualEffects.StartShake(build_standalone_shake())
            if shake_handle:
                started.append("shake")

        if started:
            set_status("Running: %s. Tune and Apply again, or press Stop." % " + ".join(started), 3)
            return

        hint = "Nothing started. "
        if state["effect_on"] and not API.VisualEffects.Enabled:
            hint += "Enable Options > Video > Visual Effects. "
        if state["shake_on"] and not API.VisualEffects.ShakeEnabled:
            hint += "Enable screen shake in Options > Video. "
        if API.VisualEffects.SlotsFree == 0:
            hint += "No effect slots are free, or you are not in the world."
        set_status(hint, 6)
    except Exception as exc:
        set_status("Error: %s" % exc, 6)
        API.SysMsg("VFX Lab: %s" % exc, 32)


def stop_effects():
    try:
        API.VisualEffects.StopAll()
        API.VisualEffects.StopAllShakes()
    except Exception as exc:
        API.SysMsg("VFX Lab: %s" % exc, 32)

    set_status("Stopped.", 3)


def print_code():
    code = build_code()
    API.SysMsg("\n" + code, 0x35)
    set_status("Code printed to the journal - copy it from there.", 4)


def close_lab():
    try:
        API.VisualEffects.StopAll()
        API.VisualEffects.StopAllShakes()
    except Exception:
        pass
    API.Stop()


# ---------------------------------------------------------------------------
# Build the window
# ---------------------------------------------------------------------------

gump = API.Gumps.CreateGump()
gump.SetRect(0, 0, WINDOW_W, WINDOW_H)
gump.CenterXInViewPort()
gump.CenterYInViewPort()
gump.SetInScreen()

gump.Add(API.Gumps.CreateGumpColorBox(0.93, "#161616").SetRect(0, 0, WINDOW_W, WINDOW_H))

title = API.Gumps.CreateGumpTTFLabel("Visual Effect Lab", 22, "#FFFFFF", maxWidth=WINDOW_W - 24)
title.SetPos(12, 9)
gump.Add(title)

status_label = API.Gumps.CreateGumpTTFLabel("", 12, "#FFFFFF", maxWidth=WINDOW_W - 24)
status_label.SetRect(12, 42, WINDOW_W - 24, 30)
gump.Add(status_label)

scroll = API.Gumps.CreateGumpScrollArea(12, 76, 496, 610)
gump.Add(scroll)

rows.append(
    CheckboxRow(scroll, "effect_on", "Visual effect enabled", True, "always",
                on_change=lambda checked: layout_rows())
)

rows.append(HeaderRow("Look", "effect"))
rows.append(
    DropdownRow(
        scroll,
        "layer_kind",
        "Layer type",
        LAYER_NAMES,
        0,
        "effect",
        on_change=lambda index: layout_rows(),
        tooltip="Tint paints colour. Blur and radial blur distort the frame. Chromatic splits the colour channels.",
    )
)
rows.append(DropdownRow(scroll, "blend", "Blend", BLEND_NAMES, 0, "effect"))
rows.append(
    CheckboxRow(
        scroll,
        "effect_fullscreen",
        "Cover the whole window, UI included",
        False,
        "effect",
        tooltip="Off draws behind the UI. On makes gumps and the cursor shake or blur too - usually unwanted.",
    )
)
rows.append(
    SliderRow(scroll, "intensity", "Intensity", 0, 100, 0.75, 0.01, _percent, "effect",
              "Overall strength passed to Start. Every layer and the fade can only scale it down.")
)
rows.append(
    SliderRow(scroll, "seconds", "Duration", 0, 60, 0, 1, _duration, "effect",
              "Zero runs until you press Stop. Anything above zero stops on its own.")
)
rows.append(SliderRow(scroll, "fade_in", "Fade in", 0, 300, DEFAULT_FADE_IN, 0.01, _hundredths_seconds, "effect"))
rows.append(SliderRow(scroll, "fade_out", "Fade out", 0, 500, DEFAULT_FADE_OUT, 0.01, _hundredths_seconds, "effect"))
rows.append(SliderRow(scroll, "strength", "Layer strength", 0, 100, DEFAULT_STRENGTH, 0.01, _percent, "effect"))

rows.append(HeaderRow("Layer", "effect"))

rows.append(HeaderRow("Tint colour", "tint"))
rows.append(SliderRow(scroll, "tint_r", "Red", 0, 255, 150, 1, None, "tint"))
rows.append(SliderRow(scroll, "tint_g", "Green", 0, 255, 30, 1, None, "tint"))
rows.append(SliderRow(scroll, "tint_b", "Blue", 0, 255, 30, 1, None, "tint"))
rows.append(SliderRow(scroll, "tint_a", "Alpha", 0, 255, 255, 1, None, "tint"))

rows.append(HeaderRow("Disk blur", "blur"))
rows.append(
    SliderRow(scroll, "blur_radius", "Radius", 0, 600, DEFAULT_BLUR_RADIUS, 0.0001, _radius, "blur",
              "Fraction of screen width, aspect corrected. Past a few percent it is frosted glass.")
)
rows.append(
    DropdownRow(scroll, "blur_taps", "Samples", TAP_NAMES, DEFAULT_BLUR_TAPS, "blur",
                tooltip="Samples per pixel. More is smoother and more expensive.")
)

rows.append(HeaderRow("Radial blur", "radial"))
rows.append(
    SliderRow(scroll, "radial_zoom", "Zoom", 0, 100, DEFAULT_RADIAL_ZOOM, 0.01, _percent, "radial",
              "How far the taps march toward the centre. The centre stays sharp at any value.")
)
rows.append(
    DropdownRow(scroll, "radial_taps", "Samples", TAP_NAMES, DEFAULT_RADIAL_TAPS, "radial",
                tooltip="Samples per pixel. Radial taps fall on a line, so fewer are usually enough.")
)

rows.append(HeaderRow("Chromatic split", "chromatic"))
rows.append(
    SliderRow(scroll, "chromatic_aberration", "Aberration", 0, 500, DEFAULT_CHROMATIC_ABERRATION, 0.0001,
              lambda value: "%.3f" % (value / 10000.0), "chromatic",
              "Red/blue separation. Fringing grows toward the corners, like a lens.")
)

rows.append(HeaderRow("Pulse", "effect"))
rows.append(
    CheckboxRow(scroll, "pulse_on", "Breathe the layer strength", False, "effect",
                on_change=lambda checked: layout_rows(),
                tooltip="Slowly swells and fades the layer. Rate is capped at 3 Hz for photosensitivity.")
)
rows.append(SliderRow(scroll, "pulse_frequency", "Rate", 0, 300, 0.5, 0.01, _hundredths_hz, "pulse"))
rows.append(SliderRow(scroll, "pulse_amplitude", "Depth", 0, 100, 0.3, 0.01, _percent, "pulse"))

rows.append(HeaderRow("Shape - advanced", "effect"))
rows.append(
    CheckboxRow(scroll, "advanced_shape", "Show shape controls", False, "effect",
                on_change=lambda checked: layout_rows(),
                tooltip="Where the effect lives and how its boundary breaks up. Leave break-up at zero for a clean edge.")
)
rows.append(
    SliderRow(scroll, "shape_reach", "Reach", 0, 100, DEFAULT_SHAPE_REACH, 0.01, _percent, "advanced_shape",
              "How far in from the screen edge the effect extends. Larger is thicker.")
)
rows.append(SliderRow(scroll, "shape_feather", "Falloff", 1, 100, DEFAULT_SHAPE_FEATHER, 0.01, _percent, "advanced_shape"))
rows.append(
    SliderRow(scroll, "shape_edge", "Vignette / border", 0, 100, DEFAULT_SHAPE_EDGE, 0.01, _percent, "advanced_shape",
              "0 is a radial vignette, 100 is a border trim. Values in between tend to favour the left and right edges.")
)
rows.append(
    SliderRow(scroll, "shape_corner", "Corner weighting", 0, 100, DEFAULT_SHAPE_CORNER, 0.01, _percent, "advanced_shape",
              "Thickens and rounds the corners of a border trim. Ignored while Vignette / border is 0.")
)
rows.append(
    SliderRow(scroll, "shape_wobble", "Drift range", 0, 15, DEFAULT_SHAPE_WOBBLE, 0.01, _percent, "advanced_shape",
              "How far the effect's centre wanders. Small values only unsteady the pivot.")
)
rows.append(
    SliderRow(scroll, "jitter_reach", "Boundary flux", 0, 100, DEFAULT_JITTER_REACH, 0.01, _percent, "advanced_shape",
              "How far the boundary can move. Anything organic wants this above 0.")
)
rows.append(
    SliderRow(scroll, "jitter_feather", "Falloff flux", 0, 100, DEFAULT_JITTER_FEATHER, 0.01, _percent, "advanced_shape")
)

rows.append(HeaderRow("Noise - advanced", "effect"))
rows.append(
    CheckboxRow(scroll, "advanced_noise", "Show noise controls", False, "effect",
                on_change=lambda checked: layout_rows(),
                tooltip="The shape of the texture inside the layer. Defaults are a soft, gently churning cloud.")
)
rows.append(
    SliderRow(scroll, "noise_base_x", "Primary freq X", 1, 100, DEFAULT_NOISE_BASE_X, 0.1, _one_decimal, "advanced_noise",
              "Primary field frequency. The X:Y ratio controls blobs versus streaks.")
)
rows.append(SliderRow(scroll, "noise_base_y", "Primary freq Y", 1, 100, DEFAULT_NOISE_BASE_Y, 0.1, _one_decimal, "advanced_noise"))
rows.append(
    SliderRow(scroll, "noise_scroll_x", "Primary drift X", -100, 100, DEFAULT_NOISE_SCROLL_X, 0.01, _two_decimals, "advanced_noise",
              "Texture-space velocity. On-screen speed is drift divided by frequency.")
)
rows.append(SliderRow(scroll, "noise_scroll_y", "Primary drift Y", -100, 100, DEFAULT_NOISE_SCROLL_Y, 0.01, _two_decimals, "advanced_noise"))
rows.append(
    DropdownRow(scroll, "base_channel", "Primary source", CHANNEL_LABELS, DEFAULT_BASE_CHANNEL, "advanced_noise",
                tooltip="Red and Green are soft organic fBm. Blue is ridged. Alpha is cell edges.")
)
rows.append(
    DropdownRow(scroll, "detail_channel", "Detail source", CHANNEL_LABELS, DEFAULT_DETAIL_CHANNEL, "advanced_noise")
)
rows.append(
    SliderRow(scroll, "noise_warp", "Churn", 0, 100, DEFAULT_NOISE_WARP, 0.01, _percent, "advanced_noise",
              "How far the primary field displaces the detail. High billows, low translates coherently.")
)
rows.append(
    SliderRow(scroll, "noise_ridge", "Ridging", 0, 100, DEFAULT_NOISE_RIDGE, 0.01, _percent, "advanced_noise",
              "Outlines the field's median. Good for cracks and filaments.")
)
rows.append(
    SliderRow(scroll, "noise_threshold", "Coverage cut-off", 0, 100, DEFAULT_NOISE_THRESHOLD, 0.01, _percent, "advanced_noise",
              "Higher keeps less, making the layer sparser.")
)
rows.append(
    SliderRow(scroll, "noise_softness", "Edge softness", 0, 100, DEFAULT_NOISE_SOFTNESS, 0.01, _percent, "advanced_noise",
              "Width of the fade at the cut-off. Small is hard-edged, large is cloud.")
)
rows.append(
    SliderRow(scroll, "noise_flat", "Solid fill", 0, 100, DEFAULT_NOISE_FLAT, 0.01, _percent, "advanced_noise",
              "Fills the shape in under the noise. Above 0 the geometric shape becomes visible.")
)

rows.append(HeaderRow("Screen shake", "always"))
rows.append(
    CheckboxRow(scroll, "shake_on", "Screen shake enabled", False, "always",
                on_change=lambda checked: layout_rows(),
                tooltip="Attached shake fires once as the effect arrives. Standalone shake runs on its own.")
)
rows.append(
    DropdownRow(scroll, "shake_mode", "Placement", ["Attached to effect", "Standalone"], 0, "shake_mode",
                on_change=lambda index: layout_rows())
)
rows.append(SliderRow(scroll, "shake_trauma", "Shake strength", 0, 100, DEFAULT_SHAKE_TRAUMA, 0.01, _percent, "shake_details"))
rows.append(SliderRow(scroll, "shake_seconds", "Shake length", 1, 300, DEFAULT_SHAKE_SECONDS, 0.01, _hundredths_seconds, "shake_details"))
rows.append(SliderRow(scroll, "shake_ramp_up", "Ramp up", 0, 300, DEFAULT_SHAKE_RAMP_UP, 0.01, _hundredths_seconds, "shake_details"))
rows.append(SliderRow(scroll, "shake_ramp_down", "Ramp down", 0, 300, DEFAULT_SHAKE_RAMP_DOWN, 0.01, _hundredths_seconds, "shake_details"))
rows.append(
    SliderRow(scroll, "shake_frequency", "Shake rate", 0, 2000, DEFAULT_SHAKE_FREQUENCY, 0.01, _shake_frequency, "shake_details",
              "Lower reads as a heavy rumble, higher as a rattle. Zero uses the client default.")
)
rows.append(
    DropdownRow(scroll, "shake_curve", "Easing", CURVE_NAMES, DEFAULT_ATTACHED_CURVE, "shake_details")
)
rows.append(
    DropdownRow(scroll, "shake_gradient", "Gradient", GRADIENT_NAMES, 0, "shake_standalone",
                tooltip="Standalone shakes only. Constant holds, Decay hits and fades, Swell builds, Pulse rises and falls.")
)
rows.append(
    SliderRow(scroll, "shake_max_offset", "Max offset", 0, 24, DEFAULT_CONFIG_MAX_OFFSET, 1, None, "shake_standalone",
              "Peak displacement in pixels. Zero uses the client's 24. Larger values are clamped.")
)
rows.append(
    CheckboxRow(scroll, "shake_fullscreen", "Shake the whole window", False, "shake_standalone",
                tooltip="Off shakes the game world only. On moves the UI and cursor too, which is hard to use.")
)

layout_rows()

code_label = API.Gumps.CreateGumpTTFLabel("Generated code", 15, "#FFFFFF", maxWidth=372)
code_label.SetPos(516, 76)
gump.Add(code_label)

code_box = API.Gumps.CreateGumpTextBox("", 372, 520, True, 11)
code_box.SetRect(516, 100, 372, 520)
code_box.SetTooltip("Select and copy this, or use Print to journal.")
gump.Add(code_box)

print_button = API.Gumps.CreateSimpleButton("Print to journal", 150, 26)
print_button.SetPos(516, 628)
gump.Add(print_button)
API.Gumps.AddControlOnClick(print_button, print_code)

warning = API.Gumps.CreateGumpTTFLabel(
    "Tuning does not change a running effect - press Apply again.\n"
    "Visual effects can flash or move the screen. Avoid rapid start/stop loops.",
    11,
    "#FFFFFF",
    maxWidth=372,
)
warning.SetRect(516, 662, 372, 36)
gump.Add(warning)

apply_button = API.Gumps.CreateSimpleButton("Apply & Start", 150, 28)
apply_button.SetPos(12, 700)
gump.Add(apply_button)
API.Gumps.AddControlOnClick(apply_button, apply_settings)

stop_button = API.Gumps.CreateSimpleButton("Stop", 100, 28)
stop_button.SetPos(172, 700)
gump.Add(stop_button)
API.Gumps.AddControlOnClick(stop_button, stop_effects)

API.Gumps.AddControlOnDisposed(gump, close_lab)
API.Gumps.AddGump(gump)

refresh_status()
refresh_preview()

next_status = 0

while not API.StopRequested and not gump.IsDisposed:
    API.ProcessCallbacks()

    if preview_dirty:
        refresh_preview()

    now = time.time()
    if now >= next_status:
        refresh_status()
        next_status = now + 1.0

    API.Pause(0.1)

try:
    API.VisualEffects.StopAll()
    API.VisualEffects.StopAllShakes()
except Exception:
    pass
