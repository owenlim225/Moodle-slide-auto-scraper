(async () => {
    const totalSlides = 11;
    const baseUrl = window.location.href.substring(0, window.location.href.lastIndexOf("/") + 1) + "data/";
    const titleHeading = "Life and Works of Rizal: A Century Hence";
    let cleanOutput = `${titleHeading}\n\n`;
    const parser = new DOMParser();

    // Anchored on "Life and Works of Rizal" so the standalone Slide 1 subtitle
    // "A Century Hence(Filipinas Dentro de Cien Años)" is preserved.
    const titlePattern = /Life\s+and\s+Works\s+of\s+Rizal\s*(?::\s*A\s+Century\s+Hence|\(\s*A\s+Century\s+Hence\s*\))/gi;
    const stripTitle = (text) => text.replace(titlePattern, '');

    const formatScrapedText = (text) => {
        let out = text.replace(/\u00A0/g, ' ');

        // Only split lower→Upper to keep acronyms (USA, NASA) intact.
        out = out.replace(/([a-z])([A-Z])/g, '$1 $2');

        out = out.replace(/([.?!:,])([A-Za-z])/g, '$1 $2');

        out = out.replace(/\?{2,}/g, '?');

        out = out.replace(/([^\n\s])\s*([•])\s*/g, '$1\n$2 ');

        // Treat '*' as a bullet only when glued between word/closing-paren and a capital,
        // so genuine multiplication or markdown emphasis would not be touched (none here).
        out = out.replace(/([\w\)])\*([A-Z])/g, '$1\n* $2');

        out = out.replace(/([a-zA-Z])\s*–\s*([A-Z])/g, '$1\n– $2');
        // Allow any non-whitespace before the dash so "ignorant?- Keeping" splits too.
        out = out.replace(/([^\s\n])-\s+([A-Z])/g, '$1\n- $2');

        // Numbered list items glued to prior text, e.g. "questions:1.Could" → "questions:\n1. Could".
        // Leading non-digit guard avoids breaking decimals like 3.14.
        out = out.replace(/([^\d\n])(\d+)\.\s+([A-Za-z])/g, '$1\n$2. $3');

        // Sentence break, but skip "1. Could" (numbered list) and decimals via the digit lookbehind.
        out = out.replace(/(?<!\d)([.?!])\s+([A-Z])/g, '$1\n$2');

        out = out.replace(/\n{3,}/g, '\n\n');

        out = out.split('\n').map(l => l.replace(/\s+$/, '')).join('\n');

        return out;
    };

    console.log("🚀 Extracting ordered text from HTML tags...");

    for (let i = 1; i <= totalSlides; i++) {
        try {
            const response = await fetch(`${baseUrl}slide${i}.js`);
            const rawFileContent = await response.text();

            const htmlMatches = rawFileContent.match(/'<div[^]*?'/g) || rawFileContent.match(/"<div[^]*?"/g);

            if (htmlMatches) {
                cleanOutput += `Slide ${i}\n${"-".repeat(10)}\n`;
                let slideTextContent = [];

                htmlMatches.forEach(match => {
                    const htmlString = match.substring(1, match.length - 1);
                    const doc = parser.parseFromString(htmlString, 'text/html');

                    const text = doc.body.innerText.trim();

                    if (text && text.length > 1) {
                        const lines = text.split(/\n+/);
                        lines.forEach(line => {
                            const trimmedLine = line.trim();
                            if (trimmedLine && !trimmedLine.includes('.png') && !trimmedLine.match(/^\d+px$/)) {
                                const cleanedLine = stripTitle(trimmedLine).trim();
                                if (cleanedLine) {
                                    slideTextContent.push(cleanedLine);
                                }
                            }
                        });
                    }
                });

                const uniqueLines = [...new Set(slideTextContent)];
                const formattedSlide = formatScrapedText(uniqueLines.join('\n')).replace(/\n+$/, '');
                cleanOutput += formattedSlide + "\n\n";
                console.log(`✅ Slide ${i} processed.`);
            }
        } catch (err) {
            console.error(`❌ Error fetching Slide ${i}`);
        }
    }

    const blob = new Blob([cleanOutput], { type: 'text/plain' });
    const el = document.createElement('a');
    el.href = URL.createObjectURL(blob);
    el.download = 'Rizal_Coursework_Final_Text.txt';
    document.body.appendChild(el);
    el.click();
    document.body.removeChild(el);

    console.log("🎉 Process complete. Your clean text file is ready.");
})();
