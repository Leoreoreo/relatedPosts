
import { sankey, sankeyCenter, sankeyLinkHorizontal } from "d3-sankey";
import React, { useState } from 'react';

const MARGIN_Y = 30;
const MARGIN_LEFT = 30;
const MARGIN_RIGHT = 100;

type Data = {
  nodes: { id: string; column: number }[];
  links: { source: string; target: string; value: number }[];
};

type SankeyProps = {
  width: number;
  height: number;
  data: Data;
  personID: number; 
};

const Sankey = ({ width, height, data, personID }: SankeyProps) => {
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const [relatedHoverNodes, setRelatedHoverNodes] = useState<Set<string>>(new Set());
  const [relatedHoverLinks, setRelatedHoverLinks] = useState<Set<string>>(new Set());
  const [clickedKeyword, setClickedKeyword] = useState<string | null>(null);
  const [clickedKeywordLinks, setClickedKeywordLinks] = useState<Set<string>>(new Set());
  const [relatedClickedAttributes, setRelatedClickedAttributes] = useState<Set<string>>(new Set());
  const [clickedAttribute, setClickedAttribute] = useState<string | null>(null);


  const sankeyGenerator = (sankey() as any) // TODO: find how to type the sankey() function
    .nodeWidth(20)
    .nodePadding(20)
    .extent([
      [MARGIN_LEFT, MARGIN_Y],
      [width - MARGIN_RIGHT, height - MARGIN_Y],
    ])
    .nodeId((node) => node.id) // Accessor function: how to retrieve the id that defines each node. This id is then used for the source and target props of links
    .nodeAlign(sankeyCenter); // Algorithm used to decide node position

  // Compute nodes and links positions
  const { nodes, links } = sankeyGenerator(data);
  const colorPalette = ['#1f77b4', '#ff7f0e', '#2ca02c'];
  // Group nodes by column and assign colors to each group
  const columnColors: { [key: number]: string } = {};
  nodes.forEach(node => {
    if (!columnColors[node.column]) {
      columnColors[node.column] = colorPalette[node.column % colorPalette.length];
    }
  });

  // Handler for mouse enter event on a node
  const handleNodeMouseEnter = (nodeId: string) => {
    const relatedHoverNodes = new Set<string>();
    const relatedHoverLinks = new Set<string>();

    const getDirectTargetNodes = (currentNode: string) => {
      const incomingLinks = links.filter(link => link.source.id === currentNode);
      incomingLinks.forEach(link => {
        const targetNode = link.target;
        relatedHoverLinks.add(link);
        relatedHoverNodes.add(targetNode);
        getDirectTargetNodes(targetNode.id);
      });
    };
    getDirectTargetNodes(nodeId);
    setHoveredNode(nodeId);
    setRelatedHoverNodes(relatedHoverNodes);
    setRelatedHoverLinks(relatedHoverLinks);
  };

  // Handler for mouse leave event on a node
  const handleNodeMouseLeave = () => {
    setRelatedHoverNodes(new Set());
    setHoveredNode(null)
  };

  const isNodeRelated = (source: string, target: string): boolean => {
    if (source === hoveredNode || target === hoveredNode) {
      return true;
    }
    const linkedNodes = links.filter(link => link.source === target).map(link => link.target);
    return linkedNodes.some(node => isNodeRelated(source, node));
  };
  
  // Handler for mouse click event on a node
  const handleNodeClick = (nodeId: string) => {
    const clickedNode = nodes.find(node => node.id === nodeId);
    const clickedKeywordLinks = new Set<string>();
    const relatedClickedAttributes = new Set<string>();

    if (!clickedNode)  {
      setClickedKeyword(null); 
      setClickedAttribute(null);
      setClickedKeywordLinks(clickedKeywordLinks)
      return;
    }
    if (clickedNode.column === 2) {
      const incomingLinks = links.filter(link => link.source.id === nodeId);
      incomingLinks.forEach(link => {
        const targetNode = link.target;
        clickedKeywordLinks.add(link);
        relatedClickedAttributes.add(targetNode);
      });

      setClickedKeyword(nodeId);
      setClickedAttribute(null);
      setClickedKeywordLinks(clickedKeywordLinks)
      setRelatedClickedAttributes(relatedClickedAttributes)
    } else if (clickedKeyword && clickedNode.column === 3) {
      setClickedAttribute(nodeId);
      setRelatedClickedAttributes(relatedClickedAttributes)
      const incomingLinks = links.filter(link => link.target.id === nodeId && link.source.id === clickedKeyword);
      if (incomingLinks.length) {
        incomingLinks.forEach(link => {clickedKeywordLinks.add(link)}); 
        setClickedKeywordLinks(clickedKeywordLinks)
      } else {
        setClickedKeyword(null); 
        setClickedAttribute(null);
        setClickedKeywordLinks(clickedKeywordLinks)
        setRelatedClickedAttributes(relatedClickedAttributes) 
      }
    } else {
      setClickedKeyword(null); 
      setClickedAttribute(null);
      setClickedKeywordLinks(clickedKeywordLinks)
      setRelatedClickedAttributes(relatedClickedAttributes)
    }
  };

  // Draw the nodes
  const allNodes = nodes.map((node) => {
    const color = columnColors[node.column];
    const isHovered = 
      hoveredNode === node.id ||
      clickedKeyword === node.id || 
      clickedAttribute === node.id || 
      relatedHoverNodes.has(node);
    const nodeSize = isHovered ? 15 : 0; 
    const opacity = isHovered || relatedClickedAttributes.has(node) ? 1 : .3; 
    const textSize = isHovered ? '20px' : '15px'; 

    return (
      <g 
        key={node.index}
        onMouseEnter={() => handleNodeMouseEnter(node.id)}
        onMouseLeave={handleNodeMouseLeave}
        onClick={() => handleNodeClick(node.id)} 
      >
        <rect
          height={node.y1 - node.y0 + nodeSize}
          width={sankeyGenerator.nodeWidth() + nodeSize}
          x={node.x0 - nodeSize / 2}
          y={node.y0 - nodeSize / 2}
          
          stroke={"white"}
          fill={color} // Use the assigned color
          fillOpacity={opacity}
          rx={2.9}
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

    const isRelatedLink = hoveredNode && 
      relatedHoverLinks.has(link) ||
      clickedKeywordLinks.has(link)
    const strokeWidth = isRelatedLink ? 15 : 10;
    const opacity = isRelatedLink ? 1 : .3;

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
      />
    );
  });

  return (
    <div>
      <h2>Sankey Chart for Person {personID}:</h2>
      <div className="svg-data-container">
        <svg width={width} height={height}>
          {allLinks}
          {allNodes}
        </svg>
        {clickedAttribute && (<div className="data-container">
            {
              <h3>{clickedKeyword}'s related data in {clickedAttribute}:</h3>
            /* {flaskOutput.length === 0 ? (
              <p>Loading...</p>
            ) :  (
              flaskOutput.map(([dataType, id, content]) => (
                <div key={`${dataType}-${id}`} className="text-item">
                  <strong>{dataType} {id}:</strong> {content}
                </div>
              ))
            )} */
            }
          </div>
        )}
      </div>
    </div>
  );
};
export default Sankey;
