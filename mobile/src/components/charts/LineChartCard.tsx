import React, { useMemo } from 'react';
import { VictoryChart, VictoryLine, VictoryTheme, VictoryAxis, VictoryGroup, VictoryArea } from 'victory-native';
import Card from '@/components/Card';
import { useTheme } from '@/theme/ThemeProvider';

type Point = { x: string | number; y: number };

type Props = {
  title?: string;
  data: Point[];
  height?: number;
};

export default function LineChartCard({ title = 'Average of Sales by month', data, height = 200 }: Props) {
  const theme = useTheme();

  const stroke = theme.colors.primary;

  const chartData = useMemo(() => data, [data]);

  return (
    <Card title={title}>
      <VictoryChart
        padding={{ top: 10, bottom: 40, left: 40, right: 16 }}
        theme={VictoryTheme.material}
        height={height}
      >
        <VictoryAxis style={{ tickLabels: { fontSize: 10, fill: theme.colors.onSurfaceVariant } }} />
        <VictoryAxis
          dependentAxis
          style={{ tickLabels: { fontSize: 10, fill: theme.colors.onSurfaceVariant } }}
        />
        <VictoryGroup>
          <VictoryArea
            data={chartData}
            style={{ data: { fill: theme.colors.primaryContainer, strokeWidth: 0 } }}
          />
          <VictoryLine data={chartData} style={{ data: { stroke, strokeWidth: 3 } }} interpolation="natural" />
        </VictoryGroup>
      </VictoryChart>
    </Card>
  );
}
