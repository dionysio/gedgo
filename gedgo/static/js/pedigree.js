var gid = d3.select("#pedigree-tree").attr("data-gid"),
    pid = d3.select("#pedigree-tree").attr("data-pid");

d3.json("/gedgo/" + gid + "/pedigree/" + pid + "/", function(treeData) {

  // Create a svg canvas
  var vis = d3.select("#pedigree-tree").append("svg:svg")
    .attr("width", 480)
    .attr("height", 600)
    .append("svg:g")
    .attr("transform", "translate(40, -100)");

  // Create a tree "canvas"
  var gid = treeData.gid;
  var tree = d3.layout.tree()
    .size([800,230]);

  var diagonal = d3.svg.diagonal()
    // change x and y (for the left to right tree)
    .projection(function(d) { return [d.y, d.x]; });

  // Preparing the data for the tree layout, convert data into an array of nodes
  var nodes = tree.nodes(treeData);
  // Create an array with all the links
  var links = tree.links(nodes);

  var link = vis.selectAll("pathlink")
    .data(links)
    .enter().append("svg:path")
    .attr("d", diagonal);

  var node = vis.selectAll("g.node")
    .data(nodes)
    .enter().append("svg:g")
    .attr("transform", function(d) {
        return "translate(" + d.y + "," + d.x + ")"; });

  // Add the dot at every node
  node.append("svg:rect")
    .attr("rx", 10)
    .attr("ry", 10)
    .attr("y", -30)
    .attr("x", -20)
    .attr("width", 200)
    .attr("height", 50);

  // place the name atribute left or right depending if children
  node.append("svg:a")
    .attr("xlink:href", function(d) { return "/gedgo/" + gid + "/" + d.id; })
    .append("text")
    .attr("dx", -10)
    .attr("dy", -10)
    .attr("text-anchor", "start")
    .text(function(d) { return d.name; })
    .attr("font-family", "Baskerville")
    .attr("font-size", "11pt");

  node.append("svg:text")
    .attr("dx", -10)
    .attr("dy", 8)
    .attr("text-anchor", "start")
    .text(function(d) { return d.span; })
    .attr("font-family", "Baskerville")
    .attr("font-size", "11pt")
    .attr("fill", "gray");
});

