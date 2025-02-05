import React, { useEffect, useState } from "react";
import { Spin, Radio, Typography, Row, Col, Input, Button } from 'antd';
import { EyeInvisibleOutlined, EyeTwoTone } from '@ant-design/icons';
const { Text } = Typography;
import axios from 'axios';

const API_URL = '/api/global_settings/1/';

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

function Field(props) {
  return (
    <Row align="middle" gutter={10}>
      <Col flex="none">
        <Text>{props.title}:</Text>
      </Col>
      <Col flex="auto">
        {React.Children.only(props.children)}
      </Col>
    </Row>);
}

export default function Settings() {
  const [settings, setSettings] = useState([]);
  const [radiusPassword, setRadiusPassword] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchSettings = () => {
    setLoading(true);
    axios.get(API_URL)
      .then((response) => {
        setSettings(response.data);
        setRadiusPassword(settings.radius_password);
        setLoading(false);
      })
      .catch((error) => {
        setSettings({enforcement_mode: 'TRUST_AND_VERIFY'});
        setLoading(false);
      });
  };

  const putSettings = () => {
    const req = fetch(API_URL, {
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
    req.then(fetchSettings);
  };

  const onEnforcementModeChange = (ev) => {
    settings.enforcement_mode = ev.target.value;
    putSettings();
  };

  const onRadiusPasswordChange = (ev) => {
    setRadiusPassword(ev.target.value);
  };

  const onRadiusPasswordSet = () => {
    settings.radius_password = radiusPassword;
    putSettings();
  };

  useEffect(fetchSettings, []);

  console.log(settings);
  return (loading ? <Spin /> :
    <>
      <Field title="Enforcement Mode">
        <Radio.Group value={settings.enforcement_mode} onChange={onEnforcementModeChange}>
          <Radio.Button value="TRUST_AND_VERIFY">Trust and Verify</Radio.Button>
          <Radio.Button value="LOCK">Lock</Radio.Button>
        </Radio.Group>
      </Field>
      <Field title="Radius Password">
        <Row>
          <Col>
            <Input.Password
              placeholder="input password"
              defaultValue={settings.radius_password}
              onChange={onRadiusPasswordChange}
              iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
            />
          </Col>
          <Col>
            <Button onClick={onRadiusPasswordSet}>Set</Button>
          </Col>
        </Row>
      </Field>
    </>
  );
}
