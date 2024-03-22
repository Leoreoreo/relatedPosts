import './Sankey.css'
import { sankey, sankeyCenter, sankeyLinkHorizontal } from "d3-sankey";
import React, { useState } from 'react';
import axios from 'axios';

const MARGIN_Y = 5;
const MARGIN_LEFT = 20;
const MARGIN_RIGHT = 70;

type Data = {
  nodes: { id: string; column: number }[];
  links: { source: string; target: string; value: number }[];
};

type SankeyProps = {
  width: number;
  height: number;
  data: Data;
  personID: number; 
  url: string;
};

const Sankey = ({ width, height, data, personID, url }: SankeyProps) => {
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const [relatedHoverNodes, setRelatedHoverNodes] = useState<Set<string>>(new Set());
  const [relatedHoverLinks, setRelatedHoverLinks] = useState<Set<string>>(new Set());
  const [clickedKeyword, setClickedKeyword] = useState<string | null>(null);
  const [clickedKeywordLinks, setClickedKeywordLinks] = useState<Set<string>>(new Set());
  const [relatedClickedAttributes, setRelatedClickedAttributes] = useState<Set<string>>(new Set());
  const [clickedAttribute, setClickedAttribute] = useState<string | null>(null);
  const [fetchedData, setFetchedData] = useState<any[]>([]);
  const sankeyGenerator = (sankey() as any)
    .nodeWidth(80)
    .nodePadding(15)
    .extent([
      [MARGIN_LEFT, MARGIN_Y],
      [width - MARGIN_RIGHT, height - MARGIN_Y],
    ])
    .nodeId((node) => node.id) // Accessor function: how to retrieve the id that defines each node. This id is then used for the source and target props of links
    .nodeAlign(sankeyCenter); // Algorithm used to decide node position

  // Compute nodes and links positions
  const { nodes, links } = sankeyGenerator(data);

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
  const sendRequestToBackend = async () => {
    try {
      setFetchedData([]);
      const response = await axios.post(url + '/RelationGraphData/', {
        keyword: clickedKeyword,
        attribute: clickedAttribute,
        selectedNumber: personID
      });
  
      const data = response.data;
      setFetchedData(data.output);
      // Handle the response data as needed
    } catch (error) {
      console.error('Error:', error);
    }
  };
  // Handler for mouse click event on a node
  const handleNodeClick = (nodeId: string) => {
    const clickedNode = nodes.find(node => node.id === nodeId);
    const clickedKeywordLinks = new Set<string>();
    const relatedClickedAttributes = new Set<string>();
    setFetchedData([]);
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
    // Check if the node has incoming or outgoing links
    const hasLinks = links.some(link => link.source === node || link.target === node);
    
    // If the node has no links, return null to skip rendering it
    if (!hasLinks) return null;
  
    
    const isHovered = 
      hoveredNode === node.id ||
      clickedKeyword === node.id || 
      clickedAttribute === node.id || 
      relatedHoverNodes.has(node);
    const nodeSize = isHovered ? 25 : 15; 
    const textSize = isHovered ? '15px' : '10px'; 
    const color = isHovered ? 'grey' : 'white';
  
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
          stroke={"black"}
          fill={color} 
          rx={2.9}
        />
        <text
          x={node.x0 + (node.x1 - node.x0) / 2} 
          y={(node.y1 + node.y0) / 2} 
          dy=".25em"
          fill="black"
          style={{fontSize: textSize, textAnchor: "middle"}}
        >
          {node.name}
        </text>
      </g>
    );
  });

  // Draw the links
  const allLinks = links.map((link, index) => {

    const isRelatedLink = hoveredNode && 
      relatedHoverLinks.has(link) ||
      clickedKeywordLinks.has(link)
    const strokeWidth = isRelatedLink ? 5 : 2;
    const opacity = isRelatedLink ? .6 : .3;

    return (
      <path
        key={index}
        d={sankeyLinkHorizontal()(link)}
        style={{
          fill: 'none',
          stroke: "black",
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
      </div>
      {clickedAttribute && (
        <div className="data-container">
          <h3>{clickedKeyword}</h3>
          <h3>{clickedAttribute}</h3>
          <br></br>
          {fetchedData.length === 0 ? (
            <button onClick={sendRequestToBackend}>Get Content</button>
          ) : (
            fetchedData.map(([dataType, id, content]) => (
              <div key={`${dataType}-${id}`} className="text-item">
                {content}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};
export default Sankey;
