import React, { useState, useEffect } from 'react';
import * as d3 from 'd3';
import { sankey as d3sankey, sankeyLinkHorizontal } from 'd3-sankey';

const SankeyChart = ({ data }) => {

  const width = 800;
  const height = 600;
  console.log(data)
  const nodes = data.nodes;
  const links = data.links;
  
  useEffect(() => {
    console.log(nodes);
    console.log(links);
    if (nodes.length > 0 && links.length > 0) {
      // Create Sankey layout
      const sankeyLayout = d3sankey()
        .nodeWidth(15)
        .nodePadding(10)
        .size([width, height]);

      const { nodes: sankeyNodes, links: sankeyLinks } = sankeyLayout({ nodes, links });


      // Create SVG container
      const svg = d3.select("#sankey-chart")
        .append("svg")
        .attr("viewBox", [0, 0, width, height]);

      // Draw links
      svg.append("g")
        .attr("fill", "none")
        .attr("stroke-opacity", 0.4)
        .selectAll("path")
        .data(sankeyLinks)
        .join("path")
        .attr("d", sankeyLinkHorizontal())
        .attr("stroke", "#000")
        .attr("stroke-width", d => Math.max(1, d.width));

      // Draw nodes
      svg.append("g")
        .selectAll("rect")
        .data(sankeyNodes)
        .join("rect")
        .attr("x", d => d.x0)
        .attr("y", d => d.y0)
        .attr("height", d => d.y1 - d.y0)
        .attr("width", d => d.x1 - d.x0)
        .attr("fill", "#69b3a2");
    }
  }, [nodes, links]);

  return <div id="sankey-chart"></div>;
};

export default SankeyChart;
