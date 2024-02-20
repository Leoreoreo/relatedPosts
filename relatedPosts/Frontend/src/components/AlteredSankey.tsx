import React from 'react';
import { sankey, sankeyCenter, sankeyLinkHorizontal } from 'd3-sankey';

const MARGIN_Y = 10;
const MARGIN_X = 50;

type Node = {
  id: string;
  column: number;
  type?: number;
};

type Link = {
  source: string;
  target: string;
};

type GraphData = {
  nodes: Node[];
  links: Link[];
};

type SankeyChartProps = {
  width: number;
  height: number;
  data: GraphData;
};

const SankeyChart: React.FC<SankeyChartProps> = ({ width, height, data }) => {
  // Set up the Sankey generator
  const sankeyGenerator = (sankey() as any) // TODO: find how to type the sankey() function
  .nodeWidth(20)
  .nodePadding(10)
  .extent([
    [MARGIN_X, MARGIN_Y],
    [width - MARGIN_X, height - MARGIN_Y],
  ])

  // Compute nodes and links positions
  const { nodes, links } = sankeyGenerator(data);

  // Draw links
  const allLinks = links.map((link, index) => (
    <path
      key={index}
      d={sankeyLinkHorizontal()(link)}
      fill="none"
      stroke="black"
      strokeWidth={1}
    />
  ));

  // Draw nodes
  const allNodes = nodes.map((node, index) => (
    <g key={index} transform={`translate(${node.x0},${node.y0})`}>
      <rect
        width={node.x1 - node.x0}
        height={node.y1 - node.y0}
        fill="#69b3a2"
        stroke="black"
      />
      <text x={-6} y={(node.y1 - node.y0) / 2} dy=".35em" textAnchor="end" fill="black">
        {node.id}
      </text>
    </g>
  ));

  return (
    <svg width={width} height={height}>
      <g>{allLinks}</g>
      <g>{allNodes}</g>
    </svg>
  );
};

export default SankeyChart;
