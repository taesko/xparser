defines = {
    'base00': '#F7B3DA',
    'base01': '#f55050',
    'base02': '#488214',
    'base03': '#EEB422',
    'base04': '#468dd4',
    'base05': '#551a8b',
    'base06': '#1b9e9e',
    'base07': '#75616b',
    'base08': '#9e8b95',
    'base09': '#e06a26',
    'base0A': '#f0dde6',
    'base0B': '#b5a3ac',
    'base0C': '#8a7680',
    'base0D': '#3b2c33',
    'base0E': '#d46a84',
    'base0F': '#2b1d24',
    'basefg': '#F0F0F0'
}

statements = {
    'URxvt*color0': '       base00',
    'URxvt*color1': '       base01',
    'URxvt*color2': '       base02',
    'URxvt*color3': '       base03',
    'URxvt*color4': '       base04',
    'URxvt*color5': '       base05',
    'URxvt*color6': '       base06',
    'URxvt*color7': '       base07',
    'URxvt*color8': '       base08',
    'URxvt*color9': '       base09',
    'URxvt*color10': '      base0A',
    'URxvt*color11': '      base0B',
    'URxvt*color12': '      base0C',
    'URxvt*color13': '      base0D',
    'URxvt*color14': '      base0E',
    'URxvt*color15': '      base0F',
    '*foreground': 'basefg',
    'URxvt*inheritPixmap': 'true',
    'URxvt*transparent': 'true',
    'URxvt*shading': '20'
}

statements = {key.strip(): value.strip() for key, value in statements.items()}
