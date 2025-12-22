
function updateTheme(bg, txt, hglt, h1, h2, h3) {
	
	var sheet = window.document.styleSheets[0];
	sheet.insertRule('.insideFl, .insideFl #frame_left, .insideFl td{ background: ' + bg + '; color: ' + txt + '}', sheet.cssRules.length);
	sheet.insertRule('.insideFl .SubTopicOf{ background: ' + bg + '}', sheet.cssRules.length);	
	sheet.insertRule('.insideFl h1{ background: ' + h1 + '}', sheet.cssRules.length);		
	sheet.insertRule('.insideFl h2{ background: ' + h2 + '}', sheet.cssRules.length);		
	sheet.insertRule('.insideFl h3{ background: ' + h3 + '}', sheet.cssRules.length);			
	sheet.insertRule('a:link, a:visited{ color: ' + hglt + '}', sheet.cssRules.length);
	sheet.insertRule('a {border-bottom-color: ' + hglt + '}', sheet.cssRules.length);
	
	window.frames[0].frameElement.contentWindow.updateTheme(bg, txt, hglt, h1, h2, h3);
}
