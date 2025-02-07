import React, { useEffect, useState } from "react";
import { StopOutlined, CheckOutlined, DeleteOutlined } from '@ant-design/icons';
import { Space, Table, Tag, Button, Spin } from 'antd';
import axios from 'axios';
import PropTypes from 'prop-types';
import { csrftoken } from './utils.js';

const API_URL = "/api/devices";

const DATE_FORMAT_OPTIONS = {
  year: "numeric",
  month: "long",
  day: "numeric",
  hour: "numeric",
  minute: "numeric",
  second: "numeric",
  timeZoneName: "short"
};

const dateFormat = new Intl.DateTimeFormat('en-US', DATE_FORMAT_OPTIONS);

export default function DeviceManagement(props) {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  let actions = [];

  const BlockAction = {
    name: 'Block',
    icon: StopOutlined,
    state: 'blocked'
  };
  const AllowAction = {
    name: 'Allow',
    icon: CheckOutlined,
    state: 'allowed'
  };
  const DeleteAction = {
    name: 'Delete',
    icon: DeleteOutlined,
    state: 'deleted'
  };

  switch (props.state) {
  case 'pending':
      actions = [BlockAction, AllowAction, DeleteAction]
      break;
  case 'blocked':
      actions = [AllowAction, DeleteAction]
      break;
  case 'allowed':
      actions = [BlockAction, DeleteAction]
      break;
  };

  const handleAction = (state, record) => {
    console.log(`handleAction: ${state} ${record.id}`);
    const url = `${API_URL}/${record.id}/`;
    let req = null;
    if (state === 'deleted') {
      req = fetch(url, {
        credentials: 'include',
        method: 'DELETE',
        mode: 'same-origin',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
        }
      });
    } else {
      req = fetch(url, {
        credentials: 'include',
        method: 'PATCH',
        mode: 'same-origin',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({'status': state})
      });
    }
    req.then(
        () => {
          axios.get(`${API_URL}/`).then(
            (response) => {setDevices(response.data);}
          )
        }
    );
  };
  const dataSource = devices.filter(d=>d['status'] === props.state).map((device, idx) => (
      {
        key: idx + 1,
        id: device.id,
        name: device.hostname,
        mac: device.mac_address,
        ip: device.ip_address,
        last_seen: device.last_seen,
      }
  ));

  const getFilters = (c) => {
      return {
        filterSearch: true,
        onFilter: (value, record) => record[c].startsWith(value),
	filters: dataSource.map((d) => { return { text: d[c], value: d[c] }; }),
      };
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      ...getFilters('name'),
    },
    {
      title: 'MAC Address',
      dataIndex: 'mac',
      key: 'mac',
      ...getFilters('mac'),
    },
    {
      title: 'IP Address',
      dataIndex: 'ip',
      key: 'ip',
      ...getFilters('ip'),
    },
    {
      title: 'Last Seen',
      dataIndex: 'last_seen',
      key: 'last_seen',
      sorter: (a, b) => new Date(a.last_seen) - new Date(b.last_seen),
      render: (_, record) => dateFormat.format(new Date(record.last_seen)),
    },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          {actions.map((a) => <Button
                               icon={React.createElement(a.icon)}
                               onClick={() => handleAction(a.state, record)}
                              >
                                {a.name}
                              </Button>)
          }
        </Space>
      ),
    },
  ];

  useEffect(() => {
    axios.get(`${API_URL}/`)
      .then((response) => {
        setDevices(response.data);
        setLoading(false);
      })
      .catch((error) => {
        setError("Failed to fetch devices.");
        setLoading(false);
      });
  }, []);

  console.log(devices);
  return (loading ? <Spin /> :
    <Table tableLayout="auto" columns={columns} dataSource={dataSource} />
  );
}

DeviceManagement.propTypes = {
  state: PropTypes.string.isRequired,
};
