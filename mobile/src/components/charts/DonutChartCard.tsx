import React from 'react';
import { View } from 'react-native';
import { VictoryPie } from 'victory-native';
import Card from '@/components/Card';
import { useTheme } from '@/theme/ThemeProvider';

type Props = {
  title?: string;
  data: { x: string; y: number; color?: string }[];
  height?: number;
  innerRadius?: number;
};

export default function DonutChartCard({ title = 'Metadata completeness', data, height = 220, innerRadius = 70 }: Props) {
  const theme = useTheme();
  const colors = data.map(d => d.color || theme.colors.primary);
  return (
    <Card title={title}>
      <View accessible accessibilityLabel={title}>
        <VictoryPie
          height={height}
          data={data}
          colorScale={colors}
          innerRadius={innerRadius}
          labels={() => ''}
          padAngle={2}
          style={{
            labels: { fill: theme.colors.text },
          }}
        />
      </View>
    </Card>
  );
}
