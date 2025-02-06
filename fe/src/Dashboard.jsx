import React, { useState } from "react";
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
    icon: React.createElement(AlertOutlined),
    label: <Link to="/pending">Pending</Link>,
  },
  {
    key: 'blocked',
    icon: React.createElement(StopOutlined),
    label: <Link to="/blocked">Blocked</Link>,
  },
  {
    key: 'allowed',
    icon: React.createElement(CheckOutlined),
    label: <Link to="/allowed">Allowed</Link>,
  },
  {
    key: 'settings',
    icon: React.createElement(SettingOutlined),
    label: <Link to="/settings">Settings</Link>,
  },
];

export default function Dashboard(props) {
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();
  const state = props.state;

  return (
    <Layout>
      <Header
        style={{
	  color: 'white',
          display: 'flex',
          alignItems: 'center',
        }}
      >
        <img src={perimeterLogo} width="60px" height="60px" />
	Perimeter
      </Header>
      <Content
        style={{
          padding: '0 48px',
        }}
      >
        <Layout
          style={{
            margin: '24px 16px',
            padding: '24px 0',
	    minHeight: "100vh",
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
          }}
        >
          <Sider
            style={{
              background: colorBgContainer,
            }}
            width={200}
          >
            <Menu
              mode="inline"
              defaultSelectedKeys={[state]}
              defaultOpenKeys={[state]}
              style={{
                height: '100%',
              }}
              items={sidebarItems}
            />
          </Sider>
          <Content
            style={{
              padding: '0 24px',
              minHeight: 280,
            }}
          >
	    {state === 'settings' ? <Settings /> : <DeviceManagement state={state} />}
          </Content>
        </Layout>
      </Content>
      <Footer
        style={{
          textAlign: 'left',
        }}
      >
	Perimeter is open source software.
      </Footer>
    </Layout>
  );
}
