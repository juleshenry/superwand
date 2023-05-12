class Img:
	pass

# https://www.losingfight.com/blog/2007/08/28/how-to-implement-a-magic-wand-tool/

def flip(img: Img, dire="vertical") -> Img:
	if dire =="vertical":
		return
	else dire = "horizontal":
		return
	else:
		return img


def clamp(o: float, mn=0,mx=1) -> o:
	return (mn if (mx if o > mx else o) < mn else o)

def gradient_boost(img: Img, style = "auto", completeness = "auto", opacity = "auto") -> Img:
	"""
	Converts monocolor regionswith directional gradient

	style : 
	~ direction of gradients
		-> auto, best guess based on boosting
		-> vertical
		-> horizontal

	completeness : 
	~impacted regions
		-> aggressive, all colors
		-> auto, most impact
		-> filter, color or set of colors
	
	opacity :
	~makes achieve minimum opacity value in region
		-> clamp {0, 1}
		-> failsafe rounds
	"""
	if style == "auto":
	else if style == "vertical":
	else if style == "horizontal":
	else:
		style == "auto"

	if completeness == "auto":
	else if completeness == "aggressive":
	else if completeness == "filter":
	else: 
		style == "auto"

	opacity = clamp(opacity, 0, 1)


	
	return img

