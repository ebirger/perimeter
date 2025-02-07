import { Link } from 'react-router';
import { AlertOutlined, StopOutlined, CheckOutlined, SettingOutlined } from '@ant-design/icons';
import { Layout, Menu, theme } from 'antd';
import DeviceManagement from "./DeviceManagement";
import Settings from "./Settings";
import perimeterLogo from '../public/perimeter.png'

const { Header, Content, Footer, Sider } = Layout;

const sidebarItems = [
  {
    key: 'pending',
    icon: <AlertOutlined />,
    label: <Link to="/pending">Pending</Link>,
  },
  {
    key: 'blocked',
    icon: <StopOutlined />,
    label: <Link to="/blocked">Blocked</Link>,
  },
  {
    key: 'allowed',
    icon: <CheckOutlined />,
    label: <Link to="/allowed">Allowed</Link>,
  },
  {
    key: 'settings',
    icon: <SettingOutlined />,
    label: <Link to="/settings">Settings</Link>,
  },
];

export default function Dashboard(props) {
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();
  const state = props.state;

  return (
    <Layout style={{ minHeight: "100vh", overflowX: "hidden" }}>
      <Header style={{ color: "white", display: "flex", alignItems: "center" }}>
        <img src={perimeterLogo} width="60px" height="60px" />
        Perimeter
      </Header>
      <Content style={{ padding: "0 16px", overflowX: "hidden" }}>
        <Layout
          style={{
            padding: "24px 0",
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
            maxWidth: "100%",
            overflowX: "hidden",
          }}
        >
          <Sider
            style={{ background: colorBgContainer }}
            collapsedWidth={0}
            breakpoint="xs"
            width={200}
          >
            <Menu
              mode="inline"
              defaultSelectedKeys={[state]}
              style={{ height: "100%", maxWidth: "100%" }}
              items={sidebarItems}
            />
          </Sider>
          <Content
            style={{
              padding: "0 16px",
              overflowX: "auto", // Ensures content scrolls instead of breaking layout
              maxWidth: "100%",
            }}
          >
            {state === "settings" ? <Settings /> : <DeviceManagement state={state} />}
          </Content>
        </Layout>
      </Content>
      <Footer style={{ textAlign: "left" }}>
        Perimeter is open source software.
      </Footer>
    </Layout>
  );
}
