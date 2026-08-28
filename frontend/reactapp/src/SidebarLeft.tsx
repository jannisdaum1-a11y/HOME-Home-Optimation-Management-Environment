import './SidebarLeft.css'

import assets from './assets/assets.json'

const excludeAssets: string[] = ['Config', "EV"];

type AssetData = {
    image?: string | null;
    [key: string]: unknown;
};
type AssetIconProps = {
    name: string,
    data: AssetData,
    onPointerStart: (name: string) => void,
}

function AssetIcon({name, data, onPointerStart}: AssetIconProps){
    const image_path = data.image;
    return (
        <div className='AssetIcon' key={name}
        onPointerDown={(event) => {
            event.preventDefault();
            onPointerStart(name);
        }}>
            <img src={image_path ?? ""} alt={name} draggable={false}/>
            <p>{name}</p>
        </div>
    )
}
type SidebarLeftProps = {
    onPointerStart: (name: string) => void,
};

function SidebarLeft({onPointerStart}: SidebarLeftProps) {
    return (
        <div className="SideBarLeft">
            {Object.entries(assets).map(([name, data]) => (
                !excludeAssets.includes(name) &&
                <AssetIcon name={name} data={data} onPointerStart={onPointerStart}></AssetIcon>
            ))}
        </div>
    );
}

export default SidebarLeft