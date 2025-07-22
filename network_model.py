import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import copy

# Load network from CSV
def load_network(file_path):
    df = pd.read_csv(file_path)
    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(row['Start'], row['End'],
                   id=row['LinkId'],
                   capacity=row['Capacity'],
                   weight=row['Weight'],
                   load=0.0)
    return G

# Find shortest path using Dijkstra
def find_shortest_path(G, source, target):
    try:
        return nx.shortest_path(G, source=source, target=target, weight='weight')
    except nx.NetworkXNoPath:
        return None

# Load traffic demands from CSV
def load_traffic(file_path):
    return pd.read_csv(file_path)

# Apply traffic and compute link loads
def apply_traffic(G, traffic_df):
    for u, v in G.edges():
        G[u][v]['load'] = 0.0

    traffic_report = []

    for _, row in traffic_df.iterrows():
        src, dst, demand = row['Source'], row['Destination'], row['Demand']
        path = find_shortest_path(G, src, dst)
        if path:
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                G[u][v]['load'] += demand
            traffic_report.append({'Source': src, 'Destination': dst, 'Demand': demand, 'Path': ' -> '.join(path)})
        else:
            traffic_report.append({'Source': src, 'Destination': dst, 'Demand': demand, 'Path': 'UNROUTABLE'})

    return pd.DataFrame(traffic_report)

# Generate link utilisation report
def link_utilisation_report(G):
    report = []
    for u, v, data in G.edges(data=True):
        utilisation_percent = (data['load'] / data['capacity']) * 100
        report.append({
            'LinkId': data['id'],
            'From': u,
            'To': v,
            'Capacity': data['capacity'],
            'Load': round(data['load'], 2),
            'Utilisation (%)': round(utilisation_percent, 2),
            'Status': 'Overloaded' if utilisation_percent > 100 else 'Critical' if utilisation_percent > 80 else 'OK'
        })
    return pd.DataFrame(report).sort_values(by='LinkId')

# Draw a single graph in its own window
def visualize_network(G, title='Network Graph'):
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(12, 8))
    plt.title(title)

    nx.draw_networkx_nodes(G, pos, node_size=700, node_color='lightblue', edgecolors='black')
    nx.draw_networkx_labels(G, pos, font_size=10, font_color='black')

    edge_colors = []
    for u, v, data in G.edges(data=True):
        utilisation = (data['load'] / data['capacity']) * 100
        if utilisation > 100:
            edge_colors.append('red')
        elif utilisation > 80:
            edge_colors.append('orange')
        else:
            edge_colors.append('green')

    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=2)

    edge_labels = {(u, v): f"{round((data['load'] / data['capacity']) * 100)}%" for u, v, data in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='black')

    red_patch = mpatches.Patch(color='red', label='Overloaded (>100%)')
    orange_patch = mpatches.Patch(color='orange', label='Critical (>80%)')
    green_patch = mpatches.Patch(color='green', label='Safe (≤80%)')
    plt.legend(handles=[green_patch, orange_patch, red_patch], loc='lower left')

    plt.axis('off')
    plt.tight_layout()
    plt.show()

# Draw each failure scenario in a subplot
def visualize_network_subplot(G, ax, title='Failure Graph'):
    pos = nx.spring_layout(G, seed=42)
    ax.set_title(title, fontsize=9)

    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=300, node_color='lightblue', edgecolors='black')
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=6, font_color='black')

    edge_colors = []
    for u, v, data in G.edges(data=True):
        utilisation = (data['load'] / data['capacity']) * 100
        if utilisation > 100:
            edge_colors.append('red')
        elif utilisation > 80:
            edge_colors.append('orange')
        else:
            edge_colors.append('green')

    nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_colors, width=1.5)

    edge_labels = {(u, v): f"{round((data['load'] / data['capacity']) * 100)}%" for u, v, data in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=5, ax=ax)

    ax.axis('off')

# Run WCF analysis and plot all failures together
def simulate_worst_case_failure(original_G, traffic_df):
    failure_summaries = []

    total_failures = original_G.number_of_edges()
    cols = 3
    rows = (total_failures // cols) + (1 if total_failures % cols else 0)

    fig, axs = plt.subplots(rows, cols, figsize=(15, 5 * rows))
    axs = axs.flatten()

    plot_index = 0

    for u, v, data in original_G.edges(data=True):
        failed_link = data['id']
        G_copy = copy.deepcopy(original_G)
        G_copy.remove_edge(u, v)

        apply_traffic(G_copy, traffic_df)
        df_util = link_utilisation_report(G_copy)
        num_unroutable = df_util['Load'].isnull().sum()
        num_overloaded = df_util[df_util['Utilisation (%)'] > 100].shape[0]
        max_util = df_util['Utilisation (%)'].max()

        failure_summaries.append({
            'Failed_Link': f"{u}-{v} (ID {failed_link})",
            'Unroutable_Flows': num_unroutable,
            'Links_Overloaded': num_overloaded,
            'Max_Utilisation (%)': round(max_util, 2)
        })

        print(f"[INFO] Simulated failure of link {failed_link} ({u}-{v})")
        visualize_network_subplot(G_copy, axs[plot_index], title=f'Fail: Link {failed_link} ({u}-{v})')
        plot_index += 1

    # Hide extra subplots if any
    for i in range(plot_index, len(axs)):
        axs[i].axis('off')

    # Add legend below all subplots
    red_patch = mpatches.Patch(color='red', label='Overloaded (>100%)')
    orange_patch = mpatches.Patch(color='orange', label='Critical (>80%)')
    green_patch = mpatches.Patch(color='green', label='Safe (≤80%)')
    plt.legend(handles=[green_patch, orange_patch, red_patch], loc='lower center', bbox_to_anchor=(0.5, -0.01), ncol=3, fontsize=10)

    plt.suptitle('Worst Case Failure - Link Failure Simulations', fontsize=14)
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    plt.show()

    return pd.DataFrame(failure_summaries).sort_values(by=['Links_Overloaded', 'Max_Utilisation (%)'], ascending=[False, False])

# MAIN
def main():
    G = load_network('network.csv')
    traffic_df = load_traffic('traffic.csv')

    print("[INFO] Running normal traffic simulation...")
    traffic_paths_df = apply_traffic(G, traffic_df)
    traffic_paths_df.to_csv('traffic_paths.csv', index=False)
    print("[INFO] Traffic paths report saved as 'traffic_paths.csv'.")

    utilisation_df = link_utilisation_report(G)
    utilisation_df.to_csv('link_utilisation.csv', index=False)
    print("[INFO] Link utilisation report saved as 'link_utilisation.csv'.")

    # Normal network visualization
    visualize_network(G, title='Normal Network Utilisation')

    print("[INFO] Running Worst Case Failure (WCF) analysis...")
    failure_df = simulate_worst_case_failure(G, traffic_df)
    failure_df.to_csv('worst_case_failures.csv', index=False)
    print("[INFO] WCF report saved as 'worst_case_failures.csv'.")

if __name__ == '__main__':
    main()
