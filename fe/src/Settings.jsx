import React, { useEffect, useState } from "react";
import PropTypes from 'prop-types';
import { Spin, Radio, Typography, Row, Col, Button, Divider } from 'antd';
import { ExportOutlined } from '@ant-design/icons';
const { Text } = Typography;
import { csrftoken } from './utils.js';

const API_URL = '/api/global_settings/1/';

const Field = (props) => {
  return (
    <Row align="middle" gutter={10}>
      <Col flex="none">
        <Text>{props.title}:</Text>
      </Col>
      <Col flex="auto">
        {React.Children.only(props.children)}
      </Col>
    </Row>);
};
Field.propTypes = {
  title: PropTypes.string.isRequired,
  children: PropTypes.element.isRequired,
};

export default function Settings() {
  const [settings, setSettings] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchSettings = async () => {
    setLoading(true);
    const resp = await fetch(API_URL);
    setLoading(false);
    if (!resp.ok) {
      setSettings({enforcement_mode: 'TRUST_AND_VERIFY'});
      return;
    }
    setSettings(await resp.json());
  };

  const putSettings = async () => {
    await fetch(API_URL, {
      credentials: 'include',
      method: 'PUT',
      mode: 'same-origin',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      },
      body: JSON.stringify(settings)
    });
    await fetchSettings();
  };

  const onEnforcementModeChange = async (ev) => {
    settings.enforcement_mode = ev.target.value;
    await putSettings();
  };

  useEffect(() => { fetchSettings(); }, []);

  return (loading ? <Spin /> :
    <>
      <Field title="Enforcement Mode">
        <Radio.Group value={settings.enforcement_mode} onChange={onEnforcementModeChange}>
          <Radio.Button value="TRUST_AND_VERIFY">Trust and Verify</Radio.Button>
          <Radio.Button value="LOCK">Lock</Radio.Button>
        </Radio.Group>
      </Field>
      <Divider />
      <Button href="/admin/" target="_blank" icon={<ExportOutlined />}>Open Django Admin</Button>
    </>
  );
}
