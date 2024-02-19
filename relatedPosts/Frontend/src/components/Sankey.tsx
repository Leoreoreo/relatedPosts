
import { sankey, sankeyCenter, sankeyLinkHorizontal } from "d3-sankey";
import React, { useState } from 'react';

const MARGIN_Y = 10;
const MARGIN_X = 50;

type Data = {
  nodes: { id: string; column: number }[]; // Include column property for each node
  links: { source: string; target: string; value: number }[];
};

type SankeyProps = {
  width: number;
  height: number;
  data: Data;
};

const Sankey = ({ width, height, data }: SankeyProps) => {
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const [relatedNodes, setRelatedNodes] = useState<Set<string>>(new Set());
  const [relatedLinks, setRelatedLinks] = useState<Set<string>>(new Set());
  const sankeyGenerator = (sankey() as any) // TODO: find how to type the sankey() function
    .nodeWidth(20)
    .nodePadding(10)
    .extent([
      [MARGIN_X, MARGIN_Y],
      [width - MARGIN_X, height - MARGIN_Y],
    ])
    .nodeId((node) => node.id) // Accessor function: how to retrieve the id that defines each node. This id is then used for the source and target props of links
    .nodeAlign(sankeyCenter); // Algorithm used to decide node position

  // Compute nodes and links positions
  const { nodes, links } = sankeyGenerator(data);
  const colorPalette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'];
  // Group nodes by column and assign colors to each group
  const columnColors: { [key: number]: string } = {};
  nodes.forEach(node => {
    if (!columnColors[node.column]) {
      columnColors[node.column] = colorPalette[node.column % colorPalette.length];
    }
  });

  // Handler for mouse enter event on a node
  const handleNodeMouseEnter = (node: string) => {
    const relatedNodes = new Set<string>();
    const relatedLinks = new Set<string>();
    const getDirectPreviousNodes = (currentNode: string) => {
      const incomingLinks = links.filter(link => link.target.id === currentNode);
      incomingLinks.forEach(link => {
        const sourceNode = link.source;
        relatedLinks.add(link);
        relatedNodes.add(sourceNode);
        getDirectPreviousNodes(sourceNode.id);
      });
    };
    const getDirectTargetNodes = (currentNode: string) => {
      const incomingLinks = links.filter(link => link.source.id === currentNode);
      incomingLinks.forEach(link => {
        const targetNode = link.target;
        relatedLinks.add(link);
        relatedNodes.add(targetNode);
        getDirectTargetNodes(targetNode.id);
      });
    };
    getDirectPreviousNodes(node);
    getDirectTargetNodes(node);
    setHoveredNode(node);
    setRelatedNodes(relatedNodes);
    setRelatedLinks(relatedLinks);
  };

  // Handler for mouse leave event on a node
  const handleNodeMouseLeave = () => {
    setRelatedNodes(new Set());
    setHoveredNode(null)
  };

  const isNodeRelated = (source: string, target: string): boolean => {
    if (source === hoveredNode || target === hoveredNode) {
      return true;
    }
    const linkedNodes = links.filter(link => link.source === target).map(link => link.target);
    return linkedNodes.some(node => isNodeRelated(source, node));
  };
  
  // Draw the nodes
  const allNodes = nodes.map((node) => {
    const color = columnColors[node.column];
    const isHovered = hoveredNode === node.id || relatedNodes.has(node);
    const nodeSize = isHovered ? 25 : 0; 
    const opacity = isHovered ? 1 : .5; 
    const textSize = isHovered ? '20px' : '15px'; 

    return (
      <g 
        key={node.index}
        onMouseEnter={() => handleNodeMouseEnter(node.id)}
        onMouseLeave={handleNodeMouseLeave}
      >
        <rect
          height={node.y1 - node.y0 + nodeSize}
          width={sankeyGenerator.nodeWidth() + nodeSize}
          x={node.x0 - nodeSize / 2}
          y={node.y0 - nodeSize / 2}
          
          stroke={"white"}
          fill={color} // Use the assigned color
          fillOpacity={opacity}
          rx={0.9}
        />
        <text
          x={node.x0 + 25} // Adjust position for text
          y={(node.y1 + node.y0) / 2 - 15} // Adjust position for text
          dy=".35em"
          fill="white"
          style={{fontSize: textSize}} // Adjust font size if needed
        >
          {node.name}
        </text>
      </g>
    );
  });

  // Draw the links
  const allLinks = links.map((link, index) => {
    const color = columnColors[link.source.column]; 

    const isRelatedLink = hoveredNode && relatedLinks.has(link)
    const strokeWidth = isRelatedLink ? 15 : 10;
    const opacity = isRelatedLink ? .8 : .5;

    return (
      <path
        key={index}
        d={sankeyLinkHorizontal()(link)}
        style={{
          fill: 'none',
          stroke: color,
          strokeWidth: strokeWidth,
          opacity: opacity,
        }}
        // onMouseEnter={() => handleLinkMouseEnter(link)}
        // onMouseLeave={handleLinkMouseLeave}

      />
    );
  });

  return (
    <div>
      <svg width={width} height={height}>
        {allLinks}
        {allNodes}
      </svg>
    </div>
  );
};
export default Sankey;
