# NodeEditor Subpage
This is a Subpage integrated into my website dedicated to the Node Editor Framework and contains information such as documentation.

My website is built to be lightweight, with as few scripts as possible and it is responsive, mobile-first and can work without javascript.
This Repository depends on the ressources found in my actual website repo.

## Sources
(see source branch)

In order to make maintaining the website easier I developed an executable tool that places the page content into a html 'frame' and replaces other generic code. It watches for changes on the source files and rebuilds the website into the build folder.
The SOURCE folder includes the pages with their content, divided in HeadLinks (links found in the header), Banner (for images and slideshow at the top of the page), Content (for all text content) and Scripts (loaded at the end of the page). Filling these regions in puts them into their respective position in the html frame.
The BUILD folders contains only additional resources (anything other than the html files in the source folder) like images, css, javascript or additional, inconsistent html pages.

In config.txt you can adjust some options aswell as specify new replacement rules (between the curly braces).

Only used tools and libraries are <a href="http://unslider.com/">Unslider</a> for the slider, <a href="https://modernizr.com/">Modernizr</a> for some conditional CSS and features and of course <a href="https://jquery.com/">jQuery</a>.

## License

This compiled page is for reference only. You may not redistribute or use it in any way without my explicit permission. Only exception is the HTML_PageBuilder executable tool in the sources branch which you may use in any way for your own projects. Additionally, the actual page content (Node Editor Documentation) found in the SOURCE folder in the sources branch, excluding the page styles and ressources found in my main webpage repo, are open for edit, but I reserve the rights for them aswell.
